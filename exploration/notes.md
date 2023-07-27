`explore.ipynb` has the items
Using ChatGPT as a co-worker

It says using a frequency based approach may work, but an ML approach may work better
    Obviously, ML is the hammer under which we crush problems

Feature detection (least to most computationally expensive):
1. Ordered chapters / preextract (*_OP_*.mkv)
    - 46/140 have ordered chapters
2. MKV chapters
    - 65/140 have chapters named "opening" or "OP" in the MKV
    - what if a series has multiple OPs? how do we check they're not all the same?
3. Subtitles (check for \ktext)
4. Subtitles (English / Signs & Songs)
    - similar frequency analysis but *LOADS* more signal
    - unfortunately anything new enough for subtitles being \ktt is also new enough for chapters
5. Audio fingerprinting (? - this seems hard)
6. Scene changes
    - limit to first five minutes?

Feature detection coverage:
Step, Covered, Cum Total
1, 46, 46
2, 65, 77
3, -, -
4, -, -

Visual Feature Detection Current plan:
     - use scenedetect to get scene changes
     - get frequency from list of scene changes -- highest frequency in the first 5 minutes is the op
     - how well does this work? BADLY. 0/140.
