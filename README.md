
Find trending keywords in job postings on The Muse, using python and dumb keyword parsing.

## To run:

- Download repository
- Install requirements.txt
- In project dir, run `python keywords.py`

## Decisions

- Narrow by category (to begin with...)
- Get all posts data before parsing, as opposed to parsing as I go.
- Assume everything is in English and I don't have to deal with real Unicode.

## Next Steps

- Real webapp with real dropdowns and no typing for the user :D
- Use actual library / algorithm for processing text and getting trending keywords / phrases.
- Better error handling, UX for exceptions.
- Option to query by location -- I started doing this but locations list was too long for a console UI :(
- Cache results nightly instead of fetching live! I would write a script for this, run API queries in blocks, etc etc...
- Other performance improvements, keep a heap of top keywords instead of having to reverse sort all the words.
- Category specific word exclusions, e.g. can filter "engineers" out of Engineering category.
- Handle real unicode...
