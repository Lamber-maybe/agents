# Hugo site fixture

PaperMod theme is not vendored. Before running eval 1:

    git clone --depth 1 https://github.com/adityatelange/hugo-PaperMod.git my-blog/themes/PaperMod

Deliberate deficiencies: beginner hugo.toml (no enableRobotsTXT / env / description /
ShowFullTextinRSS / schema / images / hasCJKLanguage), posts missing descriptions and
tags, a CJK filename post, a referenced image that doesn't exist in static/.
