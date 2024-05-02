import re
import sys
import unicodedata

from lm_eval.filters.extraction import Filter, RegexFilter

# Copied from Master
def doc_to_text(doc) -> str:
    prompt = """
    Question: {question}
    Choices:
      A. {A}
      B. {B}
      C. {C}
      D. {D}
    
    You should provide a small description of the question and the choices. You shall then
    answer the question by selecting the correct choice. You answer should have the following format:

    ```
    Justification
    
    Answer: <A/B/C/D>.
    ```
    """
    choices = [doc["opa"], doc["opb"], doc["opc"], doc["opd"]]

    prompt = prompt.format(
        A=choices[0],
        B=choices[1],
        C=choices[2],
        D=choices[3], 
        question=doc["question"]
    )

    return prompt

def doc_to_target(doc) -> str:
    return ["A", "B", "C", "D"][doc["cop"]]

class ExtendedRegexFilter(RegexFilter):
    punct_tbl = dict.fromkeys(
        i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith("P")
    )

    def __init__(
        self,
        regex_pattern: str = r"#### (\-?[0-9\.\,]+)",
        group_select=0,
        fallback: str = "[invalid]",
        ignore_case=False,
        ignore_punctuation=False,
        regexes_to_ignore=None,
    ) -> None:
        super().__init__(regex_pattern, group_select, fallback)
        self.ignore_case = ignore_case
        self.ignore_punctuation = ignore_punctuation
        self.regexes_to_ignore = regexes_to_ignore

    def filter_ignores(self, st):
        if self.regexes_to_ignore is not None:
            for s in self.regexes_to_ignore:
                st = re.sub(s, "", st)

        if self.ignore_case:
            st = st.lower()

        if self.ignore_punctuation:
            # https://stackoverflow.com/a/266162
            st = st.translate(self.punct_tbl)
        return st

    def find_match(self, regex, resp, convert_dict={}):
        match = regex.findall(resp)
        if match:
            match = match[self.group_select]
            if isinstance(match, tuple):
                match = [m for m in match if m][0]
            match = match.strip()
            if match and match in convert_dict:
                match = convert_dict[match]
        return match
