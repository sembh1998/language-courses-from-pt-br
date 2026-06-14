---
description: Concatenate selected topic combined PDFs
---
Run `scripts/concat-topics.sh $ARGUMENTS` from the project root. If no course is specified, the script uses `courses/de-from-pt-br`.

Use this when I ask for `/concat 18 26` or any other selected topic numbers/folders. When exactly two numeric arguments are provided, treat them as an inclusive range, so `/concat 18 26` means topics 18 through 26. When three or more arguments are provided, treat them as an explicit list. The script combines the selected topics' `combined.pdf` files into one PDF under `courses/<course-id>/output/pdf/concat/`, compiling an individual topic first when its `combined.pdf` is missing.

After running it, report only the generated output path and any error that needs my attention. Do not edit topic content or roadmap files.
