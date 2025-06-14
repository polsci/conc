"""Text document display class."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/api/78_text.ipynb.

# %% ../nbs/api/78_text.ipynb 3
from __future__ import annotations
from fastcore.basics import patch
import numpy as np
from IPython.display import display, HTML
import polars as pl

# %% auto 0
__all__ = ['Text']

# %% ../nbs/api/78_text.ipynb 5
from .result import Result

# %% ../nbs/api/78_text.ipynb 7
class Text:
	""" Class to represent text documents """
	def __init__(self,
			  tokens:np.ndarray, # list of token strs
			  has_spaces: np.ndarray, # whether token strs followed by space
			  metadata: dict = {} # metadata for doc as a dict
			  ): 
		self.tokens = tokens
		self.has_spaces = has_spaces
		self.metadata = metadata

# %% ../nbs/api/78_text.ipynb 8
@patch
def _nl2br(self:Text,
           text:str # document text
           ):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.replace('\n', '<br>\n')

# %% ../nbs/api/78_text.ipynb 9
@patch
def _div(self:Text,
         text:str, # document text
         class_str:str = '' # div class
         ):
    """ Wrap text in div, with optional class """
    if class_str != '':
        class_str = f' class="{class_str}"'
    return f'<div{class_str}>{text}</div>'

# %% ../nbs/api/78_text.ipynb 10
@patch
def as_string(self:Text,
              max_tokens: int|None = None # maximum length of text to display in tokens, if None, display all
        ):
    """ Return the text as a string """

    interleaved = np.empty((self.tokens.size + self.has_spaces.size,), dtype=self.tokens.dtype)
    interleaved[0::2] = self.tokens
    interleaved[1::2] = np.where(self.has_spaces, ' ', '')

    if max_tokens is not None and self.tokens.size > max_tokens:
        interleaved = interleaved[:max_tokens * 2]
        interleaved[-1] = ''

    return ''.join(list(interleaved))

# %% ../nbs/api/78_text.ipynb 11
@patch
def as_tokens(self:Text,
        ):
    """ Return the text as a tokens """

    return list(self.tokens)

# %% ../nbs/api/78_text.ipynb 12
@patch
def __str__(self:Text):
    return self.as_string()

# %% ../nbs/api/78_text.ipynb 13
@patch
def tokens_count(self:Text):
    return len(self.tokens)

# %% ../nbs/api/78_text.ipynb 14
@patch
def display_metadata(self:Text,
                ):
    """ Output the metadata for a text """

    Result('metadata', self.metadata.transpose(include_header = True, header_name = 'attribute', column_names = ['value']), 'Metadata', '', {}, []).display()


# %% ../nbs/api/78_text.ipynb 15
@patch
def display(self:Text,
			show_metadata: bool = True, # whether to display Metadata for the text
			max_tokens: int|None = None # maximum length of text to display in tokens, if None, display all
				):
	""" Output a text """
	style = '<style>.conc-text {white-space: pre-wrap;}</style>\n'
	if show_metadata:
		self.display_metadata()

	text_string = self.as_string(max_tokens = max_tokens)

	if max_tokens is not None and self.tokens.size > max_tokens:
		text_string += f'… [{max_tokens} of {self.tokens.size} tokens]'

	display(HTML(style + self._div(text_string, class_str = 'conc-text')))

