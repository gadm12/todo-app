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

        # Try multiple preprocessing approaches
        # Option A: Adaptive threshold (current)
        thresh1 = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Option B: Sharpen the image first
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        thresh2 = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Option C: Denoise first
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        thresh3 = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # For now, use the sharpened version
        return img, gray, thresh2

    def detect_layout_type(self, thresh):
        """
        Detect if schedule is grid-based or list-based.
        """

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        detect_horizontal = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
        )
        h_lines = cv2.findContours(
            detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[0]

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

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            if w > min_width and h > min_height:
                text_regions.append({"x": x, "y": y, "w": w, "h": h, "area": w * h})

        return text_regions

    def group_regions_into_rows(self, regions, y_tolerance=15):
        """
        Group text regions that are on the same horizontal line (row).
        """

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

        x_positions = []
        for row in rows:
            for region in row:
                x_positions.append(region["x"])

        x_positions.sort()
        columns = []
        current_col = [x_positions[0]]

        for x in x_positions[1:]:
            if x - current_col[-1] < 50:
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

        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img.shape[1] - x, w + 2 * padding)
        h = min(img.shape[0] - y, h + 2 * padding)

        roi = img[y : y + h, x : x + w]

        result = self.reader.readtext(roi, detail=0)
        text = " ".join(result).strip()

        return text

    def parse_schedule(self, image_path, debug=False):
        """
        Main parsing function that handles different layout types.
        """

        img, gray, thresh = self.preprocess_image(image_path)

        if debug:
            cv2.imwrite("uploads/modified/debug_thresh.png", thresh)

        layout_type = self.detect_layout_type(thresh)
        print(f"Detected layout type: {layout_type}")

        ocr_results = self.reader.readtext(image_path, detail=1)

        regions = []
        for bbox, text, conf in ocr_results:
            x = int(bbox[0][0])
            y = int(bbox[0][1])
            w = int(bbox[2][0] - bbox[0][0])
            h = int(bbox[2][1] - bbox[0][1])

            regions.append(
                {"x": x, "y": y, "w": w, "h": h, "text": text, "confidence": conf}
            )

        rows = self.group_regions_into_rows(regions)

        if debug:
            print(f"\nFound {len(rows)} rows:")
            for i, row in enumerate(rows):
                row_text = " | ".join([r["text"] for r in row])
                print(f"Row {i}: {row_text}")

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
        last_day_found = None
        last_date_seen = None
        last_time_saved = None
        pending_times = None  # NEW: Store times that don't belong to last day

        for idx, row in enumerate(rows):
            row_text = " ".join([r["text"] for r in row])

            # PRE-PROCESS: Fix common OCR mistakes
            row_text = re.sub(r"\b[Ii]am\b", "1am", row_text, flags=re.IGNORECASE)
            row_text = re.sub(r"\b[Ii]pm\b", "1pm", row_text, flags=re.IGNORECASE)
            row_text = re.sub(r"\blam\b", "1am", row_text, flags=re.IGNORECASE)
            row_text = re.sub(r"\blpm\b", "1pm", row_text, flags=re.IGNORECASE)

            print(f"DEBUG Row {idx}: '{row_text}'")

            # Look for day name
            day_found = None
            for day_variant, day_canonical in day_variations.items():
                if re.search(rf"\b{day_variant}\b", row_text, re.IGNORECASE):
                    day_found = day_canonical
                    break

            # Look for date number
            date_match = re.search(r"\b(\d{1,2})\b", row_text)
            date_num = (
                int(date_match.group(1))
                if date_match and 1 <= int(date_match.group(1)) <= 31
                else None
            )

            # Check for time patterns
            time_patterns = [
                r"(\d{1,2})\s*(?:a\.?m\.?|p\.?m\.?)\s*[-–—:]\s*(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)",
                r"(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)\s+(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)",
            ]

            time_match = None
            pattern_used = None

            for pattern in time_patterns:
                time_match = re.search(pattern, row_text, re.IGNORECASE)
                if time_match:
                    pattern_used = pattern
                    break

            print(
                f"  Day: {day_found}, Date: {date_num}, Time: {bool(time_match)}, LastDay: {last_day_found}, LastDate: {last_date_seen}"
            )

            # NEW: Check for inferred day with pending times
            if (
                date_num
                and last_date_seen
                and date_num == last_date_seen + 1
                and not day_found
            ):
                if last_day_found:
                    last_day_idx = days_order.index(last_day_found)
                    inferred_day = days_order[(last_day_idx + 1) % 7]

                    print(
                        f"  🎯 INFERRED: Date {date_num} = {inferred_day} (after {last_day_found} date {last_date_seen})"
                    )

                    # Use pending times if available, otherwise use last saved times
                    if pending_times and inferred_day not in schedule:
                        schedule[inferred_day] = pending_times
                        print(
                            f"  ✅ Assigned {inferred_day}: {schedule[inferred_day]} (from pending)"
                        )
                        pending_times = None  # Clear pending
                    elif last_time_saved and inferred_day not in schedule:
                        schedule[inferred_day] = last_time_saved
                        print(
                            f"  ✅ Assigned {inferred_day}: {schedule[inferred_day]} (from last saved)"
                        )

            if day_found:
                last_day_found = day_found
                if date_num:
                    last_date_seen = date_num
                    print(f"  📅 Mapped date {date_num} → {day_found}")

                if re.search(r"Not\s+Scheduled", row_text, re.IGNORECASE):
                    print(
                        f"  → Found 'Not Scheduled' for {day_found}, waiting for next row..."
                    )
                    schedule[day_found] = "Not Scheduled"  # Save it as Not Scheduled
                    continue
                elif time_match:
                    # Process time normally
                    start_hour = time_match.group(1)

                    if pattern_used == time_patterns[0]:
                        end_hour = time_match.group(2)
                        end_period_raw = time_match.group(3)
                    else:
                        end_hour = time_match.group(3)
                        end_period_raw = time_match.group(4)

                    end_period = end_period_raw.replace(".", "").strip().lower()

                    matched_text = time_match.group(0).lower()
                    first_time_part = (
                        matched_text.split()[0]
                        if " " in matched_text
                        else matched_text[: len(start_hour) + 3]
                    )

                    start_period = (
                        "pm"
                        if ("pm" in first_time_part or "p.m" in first_time_part)
                        else "am"
                    )

                    # OCR CORRECTION
                    start_int = int(start_hour)
                    end_int = int(end_hour)

                    if (
                        end_int == 1
                        and end_period == "am"
                        and start_int >= 2
                        and start_period == "am"
                    ):
                        print(
                            f"  ⚠️  OCR Correction for {day_found}: {end_hour}am → 11am"
                        )
                        end_hour = "11"

                    time_str = f"{start_hour}{start_period} - {end_hour}{end_period}"
                    schedule[day_found] = time_str
                    last_time_saved = time_str
                    pending_times = None  # Clear pending since we used it
                    print(f"  → Saved {day_found}: {schedule[day_found]}")

            elif time_match and last_day_found:
                # Check if last day was "Not Scheduled" - if so, these times are for the NEXT day
                if (
                    last_day_found in schedule
                    and schedule[last_day_found] == "Not Scheduled"
                ):
                    print(
                        f"  💾 Found orphaned time after 'Not Scheduled', storing for next day..."
                    )

                    # Parse and store the times
                    start_hour = time_match.group(1)

                    if pattern_used == time_patterns[0]:
                        end_hour = time_match.group(2)
                        end_period_raw = time_match.group(3)
                    else:
                        end_hour = time_match.group(3)
                        end_period_raw = time_match.group(4)

                    end_period = end_period_raw.replace(".", "").strip().lower()
                    matched_text = time_match.group(0).lower()
                    first_time_part = (
                        matched_text.split()[0]
                        if " " in matched_text
                        else matched_text[: len(start_hour) + 3]
                    )
                    start_period = (
                        "pm"
                        if ("pm" in first_time_part or "p.m" in first_time_part)
                        else "am"
                    )

                    # OCR CORRECTION
                    start_int = int(start_hour)
                    end_int = int(end_hour)
                    if (
                        end_int == 1
                        and end_period == "am"
                        and start_int >= 2
                        and start_period == "am"
                    ):
                        print(f"  ⚠️  OCR Correction: {end_hour}am → 11am")
                        end_hour = "11"

                    pending_times = (
                        f"{start_hour}{start_period} - {end_hour}{end_period}"
                    )
                    print(f"  → Pending times: {pending_times}")
                else:
                    # Normal orphaned time - assign to last day
                    print(f"  📍 Found orphaned time, assigning to {last_day_found}")

                    start_hour = time_match.group(1)

                    if pattern_used == time_patterns[0]:
                        end_hour = time_match.group(2)
                        end_period_raw = time_match.group(3)
                    else:
                        end_hour = time_match.group(3)
                        end_period_raw = time_match.group(4)

                    end_period = end_period_raw.replace(".", "").strip().lower()
                    matched_text = time_match.group(0).lower()
                    first_time_part = (
                        matched_text.split()[0]
                        if " " in matched_text
                        else matched_text[: len(start_hour) + 3]
                    )
                    start_period = (
                        "pm"
                        if ("pm" in first_time_part or "p.m" in first_time_part)
                        else "am"
                    )

                    # OCR CORRECTION
                    start_int = int(start_hour)
                    end_int = int(end_hour)
                    if (
                        end_int == 1
                        and end_period == "am"
                        and start_int >= 2
                        and start_period == "am"
                    ):
                        print(
                            f"  ⚠️  OCR Correction for {last_day_found}: {end_hour}am → 11am"
                        )
                        end_hour = "11"

                    time_str = f"{start_hour}{start_period} - {end_hour}{end_period}"
                    schedule[last_day_found] = time_str
                    last_time_saved = time_str
                    print(f"  → Saved {last_day_found}: {schedule[last_day_found]}")

        # Fill in missing days
        for day in days_order:
            if day not in schedule:
                schedule[day] = "Not Scheduled"

        return schedule


def main():
    parser = ScheduleParser()

    IMAGE_PATH = "test2.png"
    schedule = parser.parse_schedule(IMAGE_PATH, debug=True)

    print("\n" + "=" * 50)
    print("PARSED SCHEDULE")
    print("=" * 50)
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days_order:
        print(f"{day}: {schedule.get(day, 'Not Scheduled')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
