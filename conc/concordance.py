"""Functionality for concordance analysis."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/api/72_concordance.ipynb.

# %% ../nbs/api/72_concordance.ipynb 3
from __future__ import annotations
import time
import numpy as np
import polars as pl
import math
from fastcore.basics import patch
import msgspec
from IPython.display import display, HTML

# %% auto 0
__all__ = ['Concordance']

# %% ../nbs/api/72_concordance.ipynb 4
from .corpus import Corpus
from .result import Result
from .core import logger, PAGE_SIZE, EOF_TOKEN_STR, ERR_TOKEN_STR

# %% ../nbs/api/72_concordance.ipynb 8
class Concordance:
	""" Class for concordancing. """
	def __init__(self,
			  corpus:Corpus # Corpus instance
			  ): 
		self.corpus = corpus


# %% ../nbs/api/72_concordance.ipynb 9
@patch
def _get_concordance_sort(self:Concordance, 
						 token_positions: list[np.ndarray], # token index to get sort columns for
						 sort_columns: list # sort columns to use
						 ) -> tuple[np.ndarray, np.ndarray]: # token ids for first sort column and corresponding sort order
	""" Get the first sort column for a concordance. """

	start_time = time.time()
	index = 'orth_index'
	seq = np.array(token_positions[0]+sort_columns[0])
	sort_column_ids = self.corpus.get_tokens_by_index('orth_index')[seq]
	sort_column_order = self.corpus.token_ids_to_sort_order(sort_column_ids)
	logger.info(f'Concordance sort column ({sort_column_ids.shape[0]}) retrieval time: {(time.time() - start_time):.5f} seconds')
	return sort_column_ids, sort_column_order


# %% ../nbs/api/72_concordance.ipynb 14
@patch
def concordance(self: Concordance, 
				token_str: str, # token string to get concordance for 
				context_length:int = 5, # number of words to show on left and right of token string
				order:str='1R2R3R', # order of sort columns - one of 1L2L3L, 3L2L1L, 2L1L1R, 1L1R2R, 1R2R3R, LEFT, RIGHT
				page_size:int=PAGE_SIZE, # number of results to display per results page
				page_current:int=1, # current page of results
				show_all_columns:bool = False, # df with all columns or just essentials
				use_cache:bool = True # retrieve the results from cache if available (currently ignored)
				) -> Result: # concordance report results
	""" Report concordance for a token string. """

	# DONE - reducing data retrieved to just the sort columns and then doing the concordance display separately here
	# DONE - speed up the sort so that does a partial sort (e.g. just one or two columns) to get position of the slice - then handle ordering with smaller slice of data
	# IDEA: potentially get sort columns until small enough result
	
	if order not in ['1L2L3L', '3L2L1L', '2L1L1R', '1L1R2R', '1R2R3R', 'LEFT', 'RIGHT']:
		raise ValueError(f'Invalid order: order must be one of: 1L2L3L, 3L2L1L, 2L1L1R, 1L1R2R, 1R2R3R, LEFT, RIGHT')
	
	if order == 'LEFT':
		order = '1L2L3L'
	elif order == 'RIGHT':
		order = '1R2R3R'

	token_sequence, index_id = self.corpus.tokenize(token_str, simple_indexing=True)

	start_time = time.time()
	sequence_len = len(token_sequence[0])
	concordance_range = range(-1 * context_length, context_length + sequence_len)
	positional_columns = [str(x) for x in concordance_range]

	index = 'orth_index'

	use_cache = False # forcing off for now

	cache_id = tuple(['concordance'] + list(token_sequence) + [order])

	if use_cache == True and cache_id in self.corpus.results_cache:
		logger.info('Using cached concordance results')
		positional_columns = self.corpus.results_cache[cache_id][0]
		concordance_df = self.corpus.results_cache[cache_id][1]
		total_count = self.corpus.results_cache[cache_id][2]
		total_docs = self.corpus.results_cache[cache_id][3]
		sort_columns = self.corpus.results_cache[cache_id][4]
	else:
		logger.info('Processing concordance results')
		token_positions = self.corpus.get_token_positions(token_sequence, index_id)

		if len(token_positions[0]) == 0:
			logger.info('No tokens found')
			return Result(type = 'concordance', df=pl.DataFrame(), title=f'Concordance for "{token_str}"', description=f'No matches', summary_data={}, formatted_data=[])

		if order == '1L2L3L':
			sort_columns = [-1,-2,-3]
		elif order == '3L2L1L':
			sort_columns = [-3,-2,-1]
		elif order == '2L1L1R':
			sort_columns = [-2,-1,sequence_len + 1 - 1]
		elif order == '1L1R2R':
			sort_columns = [-1,sequence_len + 1 - 1,sequence_len + 2 - 1]
		else:
			# i.e. 1R2R3R
			sort_columns = [sequence_len + 1 - 1,sequence_len + 2 - 1,sequence_len + 3 - 1]

		# getting first sort column here
		sort_column_ids, sort_column_order = self._get_concordance_sort(token_positions, sort_columns)
		
		concordance_df = pl.DataFrame([pl.Series(name='index', values=token_positions[0]), pl.Series(name='sort0', values=sort_column_order), pl.Series(name=str(sort_columns[0]), values=sort_column_ids)])
		concordance_df = concordance_df.sort('sort0')
		concordance_df = concordance_df.with_row_index('row')

		total_count = len(concordance_df)
		total_docs = len(np.unique(self.corpus.get_tokens_by_index('token2doc_index')[np.array(token_positions[0])])) # REFACTORED - was using old self.corpus.token2doc_index

		self.corpus.results_cache[cache_id] = [positional_columns, concordance_df, total_count, total_docs, sort_columns]

	# working out relevant slice to populate 
	resultset_start = page_size*(page_current-1)
	resultset_len = page_size
	resultset_end = min(resultset_start + resultset_len, len(concordance_df) - 1)
	
	start_order = concordance_df['sort0'][resultset_start]
	end_order = concordance_df['sort0'][resultset_end]
	start_order_pos = concordance_df.filter(pl.col("sort0") == start_order).head(1)['row'].item()
	end_order_pos = concordance_df.filter(pl.col("sort0") == end_order).tail(1)['row'].item()
	
	# populating a smaller chunk of the concordance report - as only need to retrieve/sort a subset
	concordance_result_df = concordance_df.slice(start_order_pos, end_order_pos - start_order_pos + 1)

	results_start_time = time.time()
	concordance_columns = []
	seq = concordance_result_df['index'].to_numpy()
	for pos in concordance_range:
		tokens = self.corpus.get_tokens_by_index(index)[np.array(seq+pos)] # REFACTORED - was using getattr call to get orth_index here
		concordance_columns.append(pl.Series(name=str(pos), values=tokens))
		if pos in sort_columns:
			column_name = 'sort'+str(sort_columns.index(pos))
			if column_name != 'sort0':
				concordance_columns.append(pl.Series(name=column_name, values=self.corpus.token_ids_to_sort_order(tokens)))
	logger.info(f'Concordance results ({len(concordance_columns[0])}) retrieval time: {(time.time() - results_start_time):.5f} seconds')

	concordance_result_df = concordance_result_df.with_columns(concordance_columns)
	#offsets_arr = np.array(self.corpus.offsets,dtype=np.uint64) # FIX
	#document_ids = np.searchsorted(offsets_arr, concordance_result_df['index'], side = 'right') - 1 
	document_ids = self.corpus.get_tokens_by_index('token2doc_index')[np.array(concordance_result_df['index'])] # REFACTORED to remove offsets functionality
	concordance_result_df = concordance_result_df.with_columns(pl.Series(name="document_id", values=document_ids))
	concordance_result_df = concordance_result_df.sort(['sort0','sort1','sort2'])
		
	# slicing this further to get only the required page of results and then populating with left, keyword, right strings
	concordance_view_df = concordance_result_df.slice(start_order_pos - resultset_start, page_size)

	concordance_left = []
	concordance_right = []
	concordance_keyword = []

	for pos in positional_columns:
		if int(pos) < 0:
			concordance_left.append(self.corpus.token_ids_to_tokens(concordance_view_df[str(pos)].to_numpy()))
		elif int(pos) == 0 or int(pos) < sequence_len:
			concordance_keyword.append(self.corpus.token_ids_to_tokens(concordance_view_df[str(pos)].to_numpy()))
		else:
			concordance_right.append(self.corpus.token_ids_to_tokens(concordance_view_df[str(pos)].to_numpy()))

	concordance_left = [(' '.join(column)).split(EOF_TOKEN_STR)[-1] for column in np.array(concordance_left).T]
	concordance_keyword = [' '.join(column) for column in np.array(concordance_keyword).T]
	concordance_right = [(' '.join(column)).split(EOF_TOKEN_STR)[0] for column in np.array(concordance_right).T]

	concordance_view_df = concordance_view_df.with_columns(pl.Series(name='left', values=concordance_left), pl.Series(name='node', values=concordance_keyword), pl.Series(name='right', values=concordance_right))

	total_pages = math.ceil(total_count/page_size)
	summary_data = {'total_count': total_count, 'total_docs': total_docs, 'page': page_current, 'total_pages': total_pages}
	formatted_data = [f'Total Concordance Lines: {total_count}', f'Total Documents: {total_docs}', f'Showing {min(page_size, total_count)} lines', f'Page {page_current} of {total_pages}']

	if show_all_columns == False:
		concordance_view_df = concordance_view_df[['document_id', 'left', 'node', 'right']]
	
	logger.info(f'Concordance report time: {(time.time() - start_time):.5f} seconds')

	return Result(type = 'concordance', df=concordance_view_df, title=f'Concordance for "{token_str}"', description=f'{self.corpus.name}, Context tokens: {context_length}, Order: {order}', summary_data=summary_data, formatted_data=formatted_data)


# %% ../nbs/api/72_concordance.ipynb 23
@patch
def _get_concordance_plot_style(
	self: Concordance,
	default_font_size: int = 12, # default font size for the plot
	) -> str: # HTML styles markup
	""" Get the HTML styles for the concordance plot. """

	html_styles = '''<style>
	.conc-plot-wrapper {
	background: #fff;
	width:1000px;
	color: #000;
	font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
	line-height: 1.1;
	margin: 20px 0 20px 0;
	}
	.conc-plot-wrapper h2 {
	color: #000;
	font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
	text-align:center;
	font-weight: 600;
	line-height: 2;
	margin:0;
	padding:0;
	}
	.conc-plot-wrapper h3 {
	color: #000;
	font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
	text-align:center;
	font-weight: 300;
	line-height: 1;
	margin:0;
	padding:0;
	}
	.conc-concordance-plot {
	}
	.conc-concordance-plot-summary {
	margin: 20px 40px 10px 160px;
	color: #000;
	font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
	}
	.conc-concordance-plot-controls {
	height: 60px;
	margin: 0 40px 20px 40px;
	}
	.conc-concordance-plot-controls input[type="range"] {
	-webkit-appearance: none;
	width: 100%;
	height: 15px;
	background: #ccc;
	border-radius: 5px;
	outline: none;
	opacity: 0.7;
	transition: opacity .2s;
	}
	.conc-concordance-plot-controls label {
	font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
	color: #000;
	display: block;
	margin-bottom: 5px;
	}
	.conc-concordance-plot rect {
	fill: #ccc;
	width: 800px;
	height: 40px;
	}
	.conc-concordance-plot .label {
	font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
	}
	g.conc-concordance-plot-line {
	cursor: pointer;
	}
	g.conc-concordance-plot-line line {
	stroke:#666;
	}
	g.conc-concordance-plot-line:hover line {
	stroke:#000;
	}
	g.conc-concordance-plot-line > text {
	font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
	display:none;
	}
	g.conc-concordance-plot-line:hover > text {
	display:block;
	}
	g.conc-concordance-plot-line.highlight line {
	}
	'''
	html_styles += '.conc-plot-wrapper { font-size: ' + str(default_font_size) + 'px; }'
	html_styles += '.conc-plot-wrapper h2 { font-size: ' + str(default_font_size * 2) + 'px; }'
	html_styles += '.conc-plot-wrapper h3, .conc-concordance-plot-summary { font-size: ' + str(default_font_size * 1.25) + 'px; }'
	html_styles += '.conc-concordance-plot-controls label { font-size: ' + str(default_font_size) + 'px; }'
	html_styles += '</style>'

	return html_styles


# %% ../nbs/api/72_concordance.ipynb 24
@patch
def _get_concordance_plot_script(
	self: Concordance,
	) -> str:
	""" Get the JavaScript for the concordance plot. """

	html_script = '''
	function filter_token_ids(token_ids) {
		var centre_index = Math.floor(token_ids.length / 2);
		var left_tokens = token_ids.slice(0, centre_index);
		var right_tokens = token_ids.slice(centre_index);
		if (left_tokens.includes(eof_token)) {
			var eof_index_pos = left_tokens.lastIndexOf(eof_token);
			if (eof_index_pos !== -1) {
				left_tokens = left_tokens.slice(eof_index_pos + 1);
			}
		}
		if (right_tokens.includes(eof_token)) {
			var eof_index_pos = right_tokens.indexOf(eof_token);
			if (eof_index_pos !== -1) {
				right_tokens = right_tokens.slice(0, eof_index_pos);
			}
		}
		token_ids = left_tokens.concat(right_tokens);
		return token_ids;
	}
	function token_ids_to_str(token_ids) {
		if (token_ids.includes(eof_token)) {
			token_ids = filter_token_ids(token_ids);
		}
		const token_strs = [];
		for (let i = 0; i < token_ids.length; i++) {
			const token_id = token_ids[i];
			if (tokens[token_id]) {
				token_strs.push(tokens[token_id]);
			} else {
				token_strs.push(`Unknown Token ID: ${token_id}`);
			}
		}
		return token_strs.join(' ');
	}
	function populatePlot(page, page_size) {
		start = (page - 1) * page_size;
		end = start + page_size;
		const plot = document.getElementById('conc-concordance-plot');
		const lines = plot.getElementsByClassName('conc-concordance-plot-line');
		while (lines.length > 0) {
			lines[0].remove();
		}
		const labels = plot.getElementsByClassName('label');
		while (labels.length > 0) {
			labels[0].remove();
		}
		const rects = plot.getElementsByTagName('rect');
		for (let i = 0; i < rects.length; i++) {
			rects[i].setAttribute('style', 'opacity:1;');
		}
		for (let i = start; i < end; i++) {
			page_i = (i - start + 1)
			if (i >= docs.length) {
				const rect = document.getElementById(`rect-${page_i}`);
				if (rect) {
					rect.setAttribute('style', 'opacity:0;');
				}
				continue;
			}
			const doc = docs[i];
			const plot_y = (page_i * row_height) - row_adjustment;
			const label_y = plot_y + (default_font_size * 1.4);
			const label_y2 = plot_y + (default_font_size * 1.4 * 2);
			const doc_positions_count = doc.positions.length;
			const line_text = doc_positions_count === 1 ? '1 line' : `${doc_positions_count} lines`;
			const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
			label.setAttribute('class', 'label');
			label.setAttribute('x', label_x_right);
			label.setAttribute('y', label_y);
			label.setAttribute('font-size', default_font_size);
			label.setAttribute('text-anchor', 'end');
			label.textContent = `Doc ${doc.doc_id}`;
			plot.appendChild(label);
			const label2 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
			label2.setAttribute('class', 'label');
			label2.setAttribute('x', label_x_right);
			label2.setAttribute('y', label_y2);
			label2.setAttribute('font-size', default_font_size);
			label2.setAttribute('text-anchor', 'end');
			label2.textContent = line_text;
			plot.appendChild(label2);
			const positions = doc.positions;
			const x_values = positions.map(pos => (pos / doc.count) * 100 * 8);
			for (let j = 0; j < x_values.length; j++) {
				const x_value = x_values[j];
				const line = document.createElementNS('http://www.w3.org/2000/svg', 'g');
				line.setAttribute('class', 'conc-concordance-plot-line');
				const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
				line1.setAttribute('x1', plot_x + x_value);
				line1.setAttribute('y1', plot_y);
				line1.setAttribute('x2', plot_x + x_value);
				line1.setAttribute('y2', plot_y + subplot_height);
				line1.setAttribute('style', 'stroke-width:10;opacity:0;');
				line.appendChild(line1);
				const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
				line2.setAttribute('x1', plot_x + x_value);
				line2.setAttribute('y1', plot_y);
				line2.setAttribute('x2', plot_x + x_value);
				line2.setAttribute('y2', plot_y + subplot_height);
				line2.setAttribute('style', 'stroke-width:2;');
				line.appendChild(line2);
				let anchor = 'middle';
				let x_adjustment = 0;
				if (x_value < 150) {
					anchor = 'start';
					x_adjustment = -30;
				}
				if (x_value > 650) {
					anchor = 'end';
					x_adjustment = 30;
				}
				const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
				text.setAttribute('x', plot_x + x_value + x_adjustment);
				text.setAttribute('y', plot_y - 5);
				text.setAttribute('text-anchor', anchor);
				text.setAttribute('font-size', '12');
				text.setAttribute('fill', 'black');
				append = ''
				if (append_info) {
					position_offset_1 = doc.positions[j] + 1;
					append = ` (token ${position_offset_1} of ${doc.count})`;
				}
				text.textContent = token_ids_to_str(examples[i].orth_indices[j]) + append;
				line.appendChild(text);
				plot.appendChild(line);
			}

		}
	}

	function tryInit() {
	const targetNode = document.getElementById('conc-plot-wrapper');
	if (targetNode && targetNode.querySelector('.conc-plot-footer')) {
		vizInit();
		return true;
	}
	return false;
	}
	function vizInit() {
		current_page = 1;
		const slider = document.getElementById('conc-concordance-plot-slider');
		
		populatePlot(current_page, page_size);
		slider.addEventListener('input', function() {
			const page = parseInt(this.value, 10);
			populatePlot(page, page_size);
			const page_number = document.getElementById('conc-concordance-plot-page-number');
			page_number.textContent = `${page}`;
		});
	}
	
	'''
	return html_script

# %% ../nbs/api/72_concordance.ipynb 25
@patch
def concordance_plot(self: Concordance,
				token_str: str, # token string for concordance plot
				page_size: int = 10, # number of plots per page
				append_info: bool = True # append token position info to the concordance line preview screens visible when hover over the plot lines
				):
	"""Display a concordance plot."""

	# may make these configurable in function call in the future - but would need to ensure these don't have to passed to styles
	row_height = 60
	start_first_row_at = 30
	row_adjustment = row_height - start_first_row_at
	default_font_size = 12
	subplot_height = 40
	plot_height = start_first_row_at + (row_height * page_size) + subplot_height - row_height
	plot_x = 160
	label_x_right = plot_x - 10

	token_sequence, index_id = self.corpus.tokenize(token_str, simple_indexing=True)
	token_positions = self.corpus.get_token_positions(token_sequence, index_id)
	sequence_len = len(token_sequence[0])

	if len(token_positions[0]) == 0:
		print("No matches found.")
		return

	lines_df = self.corpus.tokens.with_row_index('position').filter(
		pl.col('position').is_in(token_positions[0])
	).select(pl.col('position'), pl.col('token2doc_index').alias('doc_id'), pl.col('orth_index').alias('orth_index_3')).sort(by = ['doc_id', 'position'])

	examples_df = lines_df

	lines_df = lines_df.join(
		self.corpus.tokens.with_row_index('position').group_by('token2doc_index').agg([
			pl.col('position').min().alias('min'),
			pl.col('position').max().alias('max')
		]).select(pl.col('token2doc_index').alias('doc_id'), pl.col('min'), pl.col('max')),
		on='doc_id',
		how='inner', #only want rows where doc_id is in lines_df
		maintain_order='left'
	)

	docs_df = lines_df.with_columns((pl.col('position') - pl.col('min')).alias('position'), (pl.col('max') - pl.col('min')).alias('count')).group_by('doc_id').agg([
		pl.col('position').alias('positions'),
		pl.col('count').first().alias('count'),
	])

	examples_df = examples_df.with_columns(
		(pl.col('position') - 3).alias('position_0'),
		(pl.col('position') - 2).alias('position_1'),
		(pl.col('position') - 1).alias('position_2'),
		(pl.col('position') + 1).alias('position_4'),
		(pl.col('position') + 2).alias('position_5'),
		(pl.col('position') + 3).alias('position_6'),
	)
	# using 3 tokens either side for initial release - see range below and hardcoded positions above - tweak so configurable in future release
	for i in range(0, 7): 
		if i == 3: # node
			continue
		else:
			examples_df = examples_df.join(
				self.corpus.tokens.with_row_index('position').select(
					pl.col('orth_index').alias(f'orth_index_{i}'),
					pl.col('position').alias(f'position_{i}')
				),
				on=f'position_{i}',
				how='inner',
				maintain_order='left'
			).drop(f'position_{i}')

	orth_index_columns = [f'orth_index_{i}' for i in range(7)]

	examples_df = examples_df.select(
		pl.col('doc_id'),
		pl.col('position'),
		*orth_index_columns
		).with_columns(pl.concat_list(orth_index_columns).alias('orth_indices')).sort(by=['doc_id', 'position'])

	unique_df = examples_df.explode('orth_indices').select(
		pl.col('orth_indices').unique().alias('token_id')
	)

	examples_df = examples_df.drop(orth_index_columns).drop('position')
	examples_df = examples_df.group_by('doc_id').agg(
		pl.concat_list(pl.col('orth_indices')).alias('orth_indices'),
	).sort(by='doc_id')
	
	unique_df = unique_df.join(
		self.corpus.vocab.select(pl.col('token_id'), pl.col('token')),
		on='token_id',
		how='left', 
		maintain_order='left'
	).sort(by='token_id')

	concordance_lines = len(token_positions[0])
	num_docs = docs_df.select(pl.len()).collect().item()
	num_pages = math.ceil(num_docs / page_size)

	html = ''
	# html = f'''<!doctype html>
	# <html lang="en">
	# <head>
	# 	<meta charset="UTF-8"><title>Conc Plot</title>
	# '''

	html += '<script>\n'
	html += f'var eof_token = {self.corpus.EOF_TOKEN};\n'
	html += f'var page_size = {page_size};\n'
	html += f'var append_info = {"true" if append_info else "false"};\n'
	html += f'var row_height = {row_height};\n'
	html += f'var start_first_row_at = {start_first_row_at};\n'
	html += f'var row_adjustment = {row_adjustment};\n'
	html += f'var default_font_size = {default_font_size};\n'
	html += f'var subplot_height = {subplot_height};\n'
	html += f'var plot_height = {plot_height};\n'
	html += f'var plot_x = {plot_x};\n'
	html += f'var label_x_right = {label_x_right};\n'
	html += 'var docs = ' + msgspec.json.encode([row for row in docs_df.collect().iter_rows(named=True)]).decode("utf-8") + ';\n'
	html += 'var tokens = ' + msgspec.json.encode({row['token_id']: row['token'] for row in unique_df.collect().iter_rows(named=True)}).decode("utf-8") + ';\n'
	html += 'var examples = ' + msgspec.json.encode([row for row in examples_df.collect().iter_rows(named=True)]).decode("utf-8") + ';\n'
	html += f'{(self._get_concordance_plot_script())}\n'
	html += '</script>\n'
	html += self._get_concordance_plot_style(default_font_size=default_font_size)
	#html += '</head><body>'

	html += '<div class="conc-plot-wrapper" id="conc-plot-wrapper">'
	html += f'<h2>Concordance Plot for &quot;{token_str}&quot;</h2>'
	html += f'<h3>{self.corpus.name}</h3>'
	html += f'<svg class="conc-concordance-plot" id="conc-concordance-plot" width="1000" height="{plot_height}" xmlns="http://www.w3.org/2000/svg">'
	# tmp
	row_adjustment = row_height - start_first_row_at
	n_plots_this_page = page_size
	for i in range(1, page_size + 1):
		html += f'<rect id="rect-{i}" x="{plot_x}" y="{((i * row_height) - row_adjustment)}" height="40" width="800" />'
	html += '</svg>'
	html += f'<div class="conc-concordance-plot-summary">Total Documents: {num_docs}<br>Total Concordance Lines: {concordance_lines}</div>'
	html += f'''<div class="conc-concordance-plot-controls"><label for="conc-concordance-plot-slider" id="conc-concordance-plot-slider-label">Page <span id="conc-concordance-plot-page-number">1</span> of {num_pages}</label>
	<input type="range" min="1" max="{num_pages}" value="1" step="1" class="slider" id="conc-concordance-plot-slider" autocomplete="off"></div>
	<div class="conc-plot-footer"></div>
	</div>'''

	html += '''
	<script>


	if (!tryInit()) {
	// Only set up observer if not ready yet
	const observer = new MutationObserver(function(mutationsList, observer) {
		if (tryInit()) {
		observer.disconnect();
		}
	});
	observer.observe(document.body, { childList: true, subtree: true });
	}
	</script>
	'''
	html += '</body></html>'

	# may add rust based minify-html here in future

	# leaving for debug option in future
	# with open('tmp.html', 'w', encoding='utf8') as f:
	# 	f.write(html)

	display(HTML(html))
	#return html	
