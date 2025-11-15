import cv2
import easyocr
import numpy as np
import re


class ScheduleParser:
    def __init__(self):
        self.reader = easyocr.Reader(["en"], gpu=False)

    def preprocess_image(self, image_path):
        """
        Preprocess image to enhance text and detect structure.
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding for better text detection
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        return img, gray, thresh

    def detect_layout_type(self, thresh):
        """
        Detect if schedule is grid-based or list-based.
        """
        # Detect horizontal lines (indicates grid layout)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        detect_horizontal = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
        )
        h_lines = cv2.findContours(
            detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[0]

        # Detect vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        detect_vertical = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
        )
        v_lines = cv2.findContours(
            detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[0]

        if len(h_lines) > 3 and len(v_lines) > 2:
            return "grid"
        else:
            return "list"

    def detect_text_regions(self, thresh, min_width=20, min_height=10):
        """
        Find bounding boxes for all text regions in the image.
        """
        # Find contours
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Filter out noise (too small regions)
            if w > min_width and h > min_height:
                text_regions.append({"x": x, "y": y, "w": w, "h": h, "area": w * h})

        return text_regions

    def group_regions_into_rows(self, regions, y_tolerance=15):
        """
        Group text regions that are on the same horizontal line (row).
        """
        # Sort by y-coordinate
        sorted_regions = sorted(regions, key=lambda r: r["y"])

        rows = []
        current_row = []
        last_y = -1000

        for region in sorted_regions:
            if last_y == -1000 or abs(region["y"] - last_y) < y_tolerance:
                current_row.append(region)
                last_y = region["y"]
            else:
                if current_row:
                    # Sort row by x-coordinate (left to right)
                    current_row.sort(key=lambda r: r["x"])
                    rows.append(current_row)
                current_row = [region]
                last_y = region["y"]

        if current_row:
            current_row.sort(key=lambda r: r["x"])
            rows.append(current_row)

        return rows

    def detect_columns(self, rows):
        """
        Detect column boundaries based on consistent x-positions across rows.
        """
        # Collect all x-positions (start of text regions)
        x_positions = []
        for row in rows:
            for region in row:
                x_positions.append(region["x"])

        # Cluster x-positions to find columns
        x_positions.sort()
        columns = []
        current_col = [x_positions[0]]

        for x in x_positions[1:]:
            if x - current_col[-1] < 50:  # Same column
                current_col.append(x)
            else:
                columns.append(int(np.mean(current_col)))
                current_col = [x]

        if current_col:
            columns.append(int(np.mean(current_col)))

        return columns

    def ocr_region(self, img, region):
        """
        Perform OCR on a specific region of the image.
        """
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]

        # Add padding
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img.shape[1] - x, w + 2 * padding)
        h = min(img.shape[0] - y, h + 2 * padding)

        roi = img[y : y + h, x : x + w]

        # Perform OCR
        result = self.reader.readtext(roi, detail=0)
        text = " ".join(result).strip()

        return text

    def parse_schedule(self, image_path, debug=False):
        """
        Main parsing function that handles different layout types.
        """
        # Load and preprocess
        img, gray, thresh = self.preprocess_image(image_path)

        if debug:
            cv2.imwrite("uploads/modified/debug_thresh.png", thresh)

        # Detect layout type
        layout_type = self.detect_layout_type(thresh)
        print(f"Detected layout type: {layout_type}")

        # Get full OCR with bounding boxes
        ocr_results = self.reader.readtext(image_path, detail=1)

        # Convert OCR results to our region format
        regions = []
        for bbox, text, conf in ocr_results:
            x = int(bbox[0][0])
            y = int(bbox[0][1])
            w = int(bbox[2][0] - bbox[0][0])
            h = int(bbox[2][1] - bbox[0][1])

            regions.append(
                {"x": x, "y": y, "w": w, "h": h, "text": text, "confidence": conf}
            )

        # Group into rows
        rows = self.group_regions_into_rows(regions)

        if debug:
            print(f"\nFound {len(rows)} rows:")
            for i, row in enumerate(rows):
                row_text = " | ".join([r["text"] for r in row])
                print(f"Row {i}: {row_text}")

        # Parse schedule from rows
        schedule = self.parse_rows_to_schedule(rows)

        return schedule

    def parse_rows_to_schedule(self, rows):
        """
        Extract schedule data from grouped rows.
        """
        days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_variations = {
            "Monday": "Mon",
            "Mon": "Mon",
            "Tuesday": "Tue",
            "Tue": "Tue",
            "Tues": "Tue",
            "Wednesday": "Wed",
            "Wed": "Wed",
            "Thursday": "Thu",
            "Thu": "Thu",
            "Thurs": "Thu",
            "Friday": "Fri",
            "Fri": "Fri",
            "Saturday": "Sat",
            "Sat": "Sat",
            "Sunday": "Sun",
            "Sun": "Sun",
        }

        schedule = {}

        for row in rows:
            # Combine text from row
            row_text = " ".join([r["text"] for r in row])

            # Look for day name
            day_found = None
            for day_variant, day_canonical in day_variations.items():
                if re.search(rf"\b{day_variant}\b", row_text, re.IGNORECASE):
                    day_found = day_canonical
                    break

            if day_found:
                # Check for "Not Scheduled"
                if re.search(r"Not\s+Scheduled", row_text, re.IGNORECASE):
                    schedule[day_found] = "Not Scheduled"
                else:
                    # Try multiple patterns to handle different OCR outputs
                    time_patterns = [
                        # Pattern 1: "2 a.m. - 11 a.m." (with dash and periods)
                        r"(\d{1,2})\s*(?:a\.?m\.?|p\.?m\.?)\s*[-–—:]\s*(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)",
                        # Pattern 2: "2am 11am" (space-separated, no dash)
                        r"(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)\s+(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)",
                    ]

                    time_match = None
                    pattern_used = None

                    for pattern in time_patterns:
                        time_match = re.search(pattern, row_text, re.IGNORECASE)
                        if time_match:
                            pattern_used = pattern
                            break

                    if time_match:
                        # Extract hours
                        start_hour = time_match.group(1)

                        # Handle different pattern structures
                        if pattern_used == time_patterns[0]:
                            # Pattern 1: (hour)(am/pm)-(hour)(am/pm)
                            end_hour = time_match.group(2)
                            end_period_raw = time_match.group(3)
                        else:
                            # Pattern 2: (hour)(am/pm) (hour)(am/pm)
                            end_hour = time_match.group(3)
                            end_period_raw = time_match.group(4)

                        # Normalize end period (remove dots, lowercase)
                        end_period = end_period_raw.replace(".", "").strip().lower()

                        # Determine start period by looking at text before the match
                        start_idx = time_match.start()
                        before_time = row_text[:start_idx].lower()

                        # Look for am/pm indicators before the start time
                        start_period = "am"  # Default to am

                        # Check the actual matched text for the start period
                        matched_text = time_match.group(0).lower()
                        first_time_part = (
                            matched_text.split()[0]
                            if " " in matched_text
                            else matched_text[: len(start_hour) + 3]
                        )

                        if "pm" in first_time_part or "p.m" in first_time_part:
                            start_period = "pm"
                        elif "am" in first_time_part or "a.m" in first_time_part:
                            start_period = "am"

                        # NORMALIZE: Always output in consistent format
                        schedule[day_found] = (
                            f"{start_hour}am - {end_hour}{end_period}"
                            if start_period == "am"
                            else f"{start_hour}pm - {end_hour}{end_period}"
                        )

                    else:
                        # No time pattern found - mark as Not Scheduled
                        schedule[day_found] = "Not Scheduled"

        # Fill in missing days
        for day in days_order:
            if day not in schedule:
                schedule[day] = "Not Scheduled"

        return schedule


def main():
    parser = ScheduleParser()

    # Parse the schedule
    IMAGE_PATH = "test2.png"
    schedule = parser.parse_schedule(IMAGE_PATH, debug=True)

    # Display results
    print("\n" + "=" * 50)
    print("PARSED SCHEDULE")
    print("=" * 50)
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days_order:
        print(f"{day}: {schedule.get(day, 'Not Scheduled')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
