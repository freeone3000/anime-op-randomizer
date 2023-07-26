`explore.ipynb` has the items
Using ChatGPT as a co-worker

It says using a frequency based approach may work, but an ML approach may work better
    Obviously, ML is the hammer under which we crush problems

Feature detection (least to most computationally expensive):
1. Chapters
2. Ordered chapters
3. Subtitles (check for \ktext)
4. Subtitles (English / Signs & Songs)
    - similar frequency analysis but *LOADS* more signal
5. Audio fingerprinting (? - this seems hard)
6. Scene changes
    - limit to first five minutes?


Visual Feature Detection Current plan:
     - use scenedetect to get scene changes
     - get frequency from list of scene changes -- highest frequency in the first 5 minutes is the op
     - how well does this work?
