# allow the script to be run standalone receiving build_process_path and build_process_batch_size as arguments
import sys
from conc.core import logger, set_logger_state
from conc.corpus import Corpus, NOT_DOC_TOKEN, INDEX_HEADER_LENGTH, EOF_TOKEN
from conc.report import Report
import time
import polars as pl
import numpy as np
import string

set_logger_state('verbose')

# from memory_profiler import profile

source_path = 'test-corpora/source/'
save_corpus_path = 'test-corpora/saved/'
test_corpora_names = [
					  'us-congressional-speeches-subset-10k', 
					  #'us-congressional-speeches-subset-100k', 
					  #'us-congressional-speeches-subset-200k', 
					  'us-congressional-speeches-subset-500k'
					  ]


# corpora = {}
# for name in test_corpora_names:
# 	try:
# 		corpora[name] = Corpus(name).build_from_csv(f'{source_path}{name}.csv.gz', text_column='text', build_process_path = 'conc-build-process')
# 	except Exception as e:
# 		raise e
	
# del corpora

from conc.corpus import nlp

# @profile
# def _complete_build_process(self: Corpus, 
# 							build_process_path: str, # path to build process
# 							slug: str # slug for the corpus
# 							):
# 	""" File-based build to create internal representation of the corpus for faster analysis and efficient representation on disk. """
# 	self.slug = slug
# 	input_df = pl.scan_parquet(f'{build_process_path}/{self.slug}/build_*.parquet')

# 	# combining indexes to reindex
# 	combined_df = pl.concat([input_df.select(pl.col('orth_index').alias('index')), input_df.select(pl.col('lower_index').alias('index'))])

# 	vocab_df  = combined_df.select(pl.col('index').unique().sort().alias('source_id')).with_row_index('token_id', offset=1).collect()
# 	logger.info(f'vocab_df: {len(vocab_df)}')

# 	combined_df = (combined_df.with_columns(pl.col('index').replace(vocab_df.select(pl.col('source_id'))['source_id'], vocab_df.select(pl.col('token_id'))['token_id']).cast(pl.UInt32)))
# 	combined_df = combined_df.with_columns(pl.col('index').cast(pl.UInt32))

# 	input_length = input_df.collect().height

# 	tokens_df = pl.concat(
# 									[combined_df.select(pl.col('index').alias('orth_index')).slice(0, input_length), 
# 									combined_df.select(pl.col('index').alias('lower_index')).slice(input_length),
# 									input_df.select(pl.col('token2doc_index'))], how='horizontal'
# 							)

# 	del combined_df
# 	del input_df

# 	vocab = {k:nlp.vocab[k].text for k in vocab_df['source_id'].to_list()}
# 	token_strs = list(vocab.values())
# 	vocab_df = vocab_df.with_columns(pl.Series(token_strs).alias('token'))

# 	self.EOF_TOKEN = vocab_df.filter(pl.col('source_id') == EOF_TOKEN)['token_id'][0] 

# 	tokens_df.collect().write_parquet(f'{build_process_path}/{self.slug}/tokens.parquet')
# 	lower_index = tokens_df.select(pl.col('lower_index')).collect().to_numpy()
# 	self.punct_tokens = [(k + 1) for k, v in enumerate(token_strs) if v.strip(string.punctuation) == '']
# 	self.space_tokens = [(k + 1) for k, v in enumerate(token_strs) if v.strip() == '']
# 	self.punct_positions = np.nonzero(np.isin(lower_index, self.punct_tokens))[0] # improve to not use lower_index and build lazily
# 	self.space_positions = np.nonzero(np.isin(lower_index, self.space_tokens))[0] # improve to not use lower_index
# 	del lower_index

# 	# get counts from tokens_df
# 	frequency_lower = tokens_df.filter(pl.col('lower_index') != self.EOF_TOKEN).select(pl.col('lower_index')).group_by('lower_index').agg(pl.count('lower_index').alias('frequency_lower')).collect()
# 	self.unique_tokens = len(frequency_lower)
# 	frequency_orth = tokens_df.filter(pl.col('orth_index') != self.EOF_TOKEN).select(pl.col('orth_index')).group_by('orth_index').agg(pl.count('orth_index').alias('frequency_orth')).collect()
# 	vocab_df = vocab_df.join(frequency_lower, left_on = 'token_id', right_on = 'lower_index', how='left').join(frequency_orth, left_on = 'token_id', right_on = 'orth_index', how='left')

# 	# add column for is_punct and is_space based on punct_tokens and space_tokens and token_id
# 	vocab_df = vocab_df.with_columns(pl.Series(np.isin(vocab_df['token_id'], self.punct_tokens)).alias('is_punct'))
# 	vocab_df = vocab_df.with_columns(pl.Series(np.isin(vocab_df['token_id'], self.space_tokens)).alias('is_space'))

# 	vocab_df.write_parquet(f'{build_process_path}/{self.slug}/vocab.parquet')

# 	self.document_count = len(tokens_df.filter(pl.col('token2doc_index') != NOT_DOC_TOKEN).select(pl.col('token2doc_index').unique()).collect())
# 	# adjusting for text breaks and jeaders at start and end of index
# 	self.token_count = input_length - self.document_count - INDEX_HEADER_LENGTH - INDEX_HEADER_LENGTH 

# 	self.word_token_count = self.token_count - len(self.punct_positions) - len(self.space_positions)
# 	self.unique_word_tokens = self.unique_tokens - len(self.punct_tokens) - len(self.space_tokens)

# 	del tokens_df



# get args
if len(sys.argv) > 1:
	if sys.argv[1] == 'None':
		build_process_path = None
	else:
		build_process_path = sys.argv[1]
	if len(sys.argv) > 2:
		build_process_batch_size = int(sys.argv[2])
	else:
		build_process_batch_size = 5000
else:
	build_process_path = None
	build_process_batch_size = 5000

logger.info(f'build_process_path: {build_process_path}')
logger.info(f'build_process_batch_size: {build_process_batch_size}')

def main():
	global nlp
	test = Corpus()
	doc_order = 0
	iterator = test._prepare_csv('test-corpora/source/us-congressional-speeches-subset-500k.csv.gz', text_column='text')
	for doc in nlp.tokenizer.pipe(iterator, batch_size=1000):
		if doc_order % 5000 == 0:
			logger.memory_usage(f'processed {doc_order} documents')
		doc_order += 1
		if doc_order > 50000:
			break
		pass

	# remove nlp
	del nlp
	logger.memory_usage(f'del nlp')
	del iterator
	logger.memory_usage(f'del iterator')
	# for name in test_corpora_names:

	# 	corpus = Corpus(name).build_from_csv(f'{source_path}{name}.csv.gz', text_column='text', build_process_path = build_process_path, build_process_batch_size = build_process_batch_size)
	# 	#_complete_build_process(corpus, build_process_path, slug = name)
	# 	del corpus
	# 	time.sleep(2)

if __name__ == '__main__':
	main()