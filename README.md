# EAGLE EYE --- AI-Assisted Electrical Cabinet Quality Inspection

> **Purpose:** Help inspectors review electrical-cabinet photographs by
> reading visible wire labels, comparing extracted values with approved
> reference data, and preparing evidence-backed quality-control
> findings.

EAGLE EYE is a computer-vision/OCR prototype concept for electrical
cabinet inspection. It is designed to **assist** an inspector, not to
certify wiring safety or replace an electrical engineer.

## Real cabinet photo

The following photo was supplied for the EAGLE EYE presentation. It
shows the kind of cabinet image the system is intended to process. The
photo is an example input; it is **not** evidence that every label in
this image has already been detected correctly by the software.

![Electrical cabinet with labelled wires and terminal
blocks](assets/electrical_cabinet_reference.png)

A copy of the unmodified supplied image is also included at
[`assets/electrical_cabinet_reference_original.png`](assets/electrical_cabinet_reference_original.png).

------------------------------------------------------------------------

## 1. The problem EAGLE EYE addresses

During a manual inspection, a technician may need to:

-   Read small wire/ferrule labels and device tags from a cabinet photo.
-   Check those values against a general-arrangement (GA) drawing, wire
    list, component list, or QC checklist.
-   Identify missing, unreadable, or mismatched labels.
-   Record the result so another person can review the evidence later.

This can be repetitive, and labels can be blurred, reflective, angled,
or partly hidden. EAGLE EYE aims to make the review more consistent by
turning image observations into structured data that can be compared
with approved references.

## 2. How the mechanism works

``` text
Cabinet photo + GA PDF + Excel wire list + QC checklist
                         |
                         v
             1. Input validation
                         |
                         v
          2. OpenCV image preprocessing
                         |
                         v
             3. Tesseract OCR
          text + confidence + coordinates
                         |
                         v
           4. Normalize and structure data
                         |
                         v
       5. Compare detected values with references
                         |
                         v
          6. PASS / FAIL / REVIEW findings
                         |
                         v
       Annotated photo + structured QC report
                         |
                         v
                Human verification
```

### Step 1 --- Image and document input

The user supplies the cabinet photograph and the project reference
documents:

-   Cabinet photo (JPG, JPEG, or PNG).
-   GA drawing (PDF).
-   Wire/label list or component list (Excel/CSV).
-   QC checklist or expected inspection rules.

The application should validate file types and report missing or
unreadable inputs before analysis starts. Reference documents should be
the approved versions for the cabinet being inspected.

### Step 2 --- Image scanning and preprocessing

OpenCV loads the image and can prepare a copy for OCR. Depending on the
photo, preprocessing may include:

1.  Check that the image loaded successfully.
2.  Convert a working copy to grayscale.
3.  Improve local contrast where needed (for example, CLAHE).
4.  Resize or threshold the image only when doing so improves
    readability.
5.  Preserve the original image so every result can be checked against
    the source.

Preprocessing does not guarantee accurate OCR. A good original photo,
even lighting, focus, and readable labels remain important.

### Step 3 --- Text and number extraction

Tesseract OCR, called through `pytesseract`, attempts to recognize
visible characters. The `image_to_data` output can provide:

-   Recognized text.
-   Confidence value from the OCR engine.
-   Bounding-box coordinates for the recognized word or text region.
-   Page/block/line/word information where available.

A simplified detection record may look like this:

``` json
{
  "text": "CBL-1007",
  "confidence": 82.0,
  "bbox": {
    "x": 245,
    "y": 318,
    "width": 96,
    "height": 24
  },
  "status": "DETECTED"
}
```

**Illustrative example only:** the label and values above are examples
of the data format, not measured output from the supplied photo. OCR
confidence is not the same as the probability that a label is correct.

### Step 4 --- Data loading and normalization

The data-loading module reads the expected values from approved
reference files. Depending on the actual implementation, this can
involve:

-   Extracting text or tables from a PDF.
-   Reading rows and columns from Excel/CSV.
-   Normalizing harmless formatting differences (such as extra spaces or
    letter case) where the project rules allow it.
-   Keeping the original value alongside the normalized value for
    traceability.

Do not silently treat similar-looking characters (for example `O` and
`0`, or `I` and `1`) as identical unless a documented rule and human
review support that decision.

### Step 5 --- Expected-versus-detected comparison

The QC engine compares OCR observations with the reference list. It
should preserve the reason for every finding.

  ----------------------------------------------------------------------------
  Status                  Meaning                      Recommended handling
  ----------------------- ---------------------------- -----------------------
  `PASS`                  The relevant check matches   Keep the comparison
                          the approved reference under evidence in the report.
                          the configured rules.        

  `FAIL`                  A discrepancy is confirmed   Highlight the issue and
                          by the configured check and  request inspector
                          sufficient evidence.         verification.

  `REVIEW`                OCR is                       Do not assume a
                          unreadable/low-confidence,   component is missing;
                          reference data is missing,   ask a person to review
                          or the result is ambiguous.  it.
  ----------------------------------------------------------------------------

A missing OCR result alone must **not** be treated as proof that a wire
or component is absent. Text recognition can read a label; by itself it
cannot prove terminal connectivity, correct placement, wire routing, or
electrical safety.

### Step 6 --- Visual evidence and report

The intended report should help a person understand each result quickly:

-   Original cabinet photo.
-   Annotated copy with OCR bounding boxes.
-   Detected label and confidence value.
-   Expected reference value and detected value.
-   `PASS`, `FAIL`, or `REVIEW` status.
-   A short explanation for a flagged item.
-   Structured output (for example JSON) and, if implemented, a
    downloadable CSV/PDF report.

Only show metrics and results that were actually produced by a run.
Mockups and example records must be labelled as illustrative.

------------------------------------------------------------------------

## 3. Proposed repository structure

The project has been organized around separate modules so each part can
be tested independently. Adjust this tree to match the files actually
present in the repository.

``` text
EAGLE-EYE/
├── app.py                 # User interface and workflow orchestration
├── vision.py              # Image loading, preprocessing, OCR and annotations
├── data_loader.py         # Loading expected values from PDF / Excel / CSV
├── qc_engine.py           # Expected-versus-detected checks and statuses
├── requirements.txt       # Python dependencies
├── input/                 # Example inputs (avoid committing sensitive data)
├── output/                # Generated annotations and reports
├── assets/
│   ├── electrical_cabinet_reference.png
│   └── electrical_cabinet_reference_original.png
└── README.md
```

### Module responsibilities

-   **`app.py`** --- Accepts uploads, calls the other modules, and
    presents the results.
-   **`vision.py`** --- Loads the cabinet image, preprocesses a working
    copy, calls OCR, collects text/confidence/bounding boxes, and saves
    an annotated image when implemented.
-   **`data_loader.py`** --- Reads expected labels and component data
    from approved PDF/Excel/CSV files and returns a consistent data
    structure.
-   **`qc_engine.py`** --- Compares expected and detected values,
    assigns a status with a reason, and returns structured findings.

Suggested data contract between modules:

``` python
{
    "detections": [
        {
            "text": "example-label",
            "confidence": 82.0,
            "bbox": {"x": 10, "y": 20, "width": 80, "height": 18}
        }
    ],
    "findings": [
        {
            "expected": "example-label",
            "detected": "example-label",
            "status": "PASS",
            "reason": "Detected value matches the reference"
        }
    ]
}
```

This is a suggested interface example. Keep it aligned with the actual
keys used by the code in the repository.

------------------------------------------------------------------------

## 4. Technology stack

  -----------------------------------------------------------------------
  Technology                          Role
  ----------------------------------- -----------------------------------
  Python                              Application and module integration

  OpenCV (`opencv-python`)            Image loading and preprocessing

  Tesseract OCR                       Optical character recognition
                                      engine

  `pytesseract`                       Python interface to Tesseract

  Pillow                              Image reading/handling where needed

  Pandas / `openpyxl`                 Spreadsheet data loading, if used

  PDF parser                          PDF reference extraction, depending
                                      on the chosen implementation

  Streamlit                           Browser-based UI, if included in
                                      `app.py`
  -----------------------------------------------------------------------

OpenCV and Tesseract are different components: OpenCV prepares and
manipulates the image; Tesseract performs OCR; `pytesseract` passes
images to the Tesseract engine and exposes its output to Python.

## 5. Setup

### Prerequisites

-   Python 3.10 or a version supported by the dependencies in the
    project.
-   Git.
-   Tesseract OCR installed separately from the Python package.
-   The project's `requirements.txt`.

### Windows

``` powershell
git clone <YOUR-REPOSITORY-URL>
cd EAGLE-EYE

py -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Tesseract OCR for Windows and note the location of
`tesseract.exe`. If it is not on your system `PATH`, configure the path
in the application, for example:

``` python
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
```

Use the path that actually exists on your computer.

### Linux

``` bash
git clone <YOUR-REPOSITORY-URL>
cd EAGLE-EYE

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install the system Tesseract package using your distribution's package
manager. For Ubuntu/Debian, this is commonly:

``` bash
sudo apt update
sudo apt install tesseract-ocr
```

### Run the application

If the repository includes a Streamlit app:

``` bash
streamlit run app.py
```

If your current version uses a different entry point, use the command
documented in that file. The command above is not a guarantee that every
module is already integrated.

------------------------------------------------------------------------

## 6. Testing plan

Test the pipeline with a small set of images and a verified reference
list before using it for inspection.

1.  **Image loading:** test a valid image, an unsupported file, and a
    corrupted image.
2.  **OCR:** test clear labels, blurred labels, glare, rotation, and
    low-light images.
3.  **Reference parsing:** test a valid spreadsheet/PDF and missing or
    malformed data.
4.  **Comparison:** include known matches, known mismatches, duplicate
    labels, and missing reference values.
5.  **Uncertainty:** verify that unreadable or ambiguous values go to
    `REVIEW`.
6.  **Reporting:** verify that each finding includes its status, reason,
    and evidence location.
7.  **Regression:** rerun the same sample set after changes and compare
    results.

Useful evaluation metrics include exact-label match rate, false-positive
count, false-negative count, percentage of findings routed to `REVIEW`,
report completeness, and processing time per image. Do not publish
numeric accuracy claims until they have been measured on a labelled test
set.

## 7. Limitations and safety

-   OCR can confuse characters and miss labels.
-   A bounding box identifies a text region; it does not establish that
    the wire is connected to the correct terminal.
-   A photograph may hide wires, labels, rear connections, or other
    relevant details.
-   A missing OCR result is not proof of a missing component.
-   Incorrect or outdated reference drawings can lead to misleading
    comparisons.
-   Electrical safety decisions must remain with qualified personnel and
    approved inspection procedures.

**EAGLE EYE is an inspection-support prototype, not a certified
electrical safety system.** Always verify flagged findings against the
physical cabinet and approved engineering documents.

## 8. Actual photo versus illustrative visuals

The image embedded above is the supplied cabinet reference photo. Any
synthetic dashboard, detection overlay, sample JSON, or example status
shown in a presentation is illustrative unless it was generated by the
running application from a recorded test. Keep this distinction clear in
demos and reports.

## 9. Contributing

1.  Create a branch for your change.
2.  Keep image processing, data loading, QC logic, and UI
    responsibilities separate.
3.  Add a test case for new comparison or parsing rules.
4.  Never commit confidential cabinet photographs, proprietary drawings,
    credentials, or customer data without permission.
5.  Document any new dependency in `requirements.txt` and this README.

## References

-   [OpenCV-Python
    tutorials](https://docs.opencv.org/5.0/py_tutorials/py_tutorials.html)
-   [Tesseract OCR API
    examples](https://tesseract-ocr.github.io/tessdoc/APIExample.html)
-   [pytesseract documentation on
    PyPI](https://pypi.org/project/pytesseract/)

------------------------------------------------------------------------

**Project name:** EAGLE EYE\
**Category:** Computer Vision · OCR · Quality Control\
**Primary goal:** Make electrical cabinet label inspection more
consistent, explainable, and traceable.
