import camelot
import sys
import os
import io
import glob
import pdftotext
from tabulate import tabulate
from pathlib import Path

def write_html(f, s):
	f.write("<pre>%s</pre>" % s)

def parse_pdf(pdf):
	print(pdf)
	pcn_id = Path(pdf).stem
	areas = [['0,660,540,540']]
	tables = camelot.read_pdf(pdf, flavor='lattice', pages='2,3', line_scale=50, strip_text='\n', resolution=600, shift_text=['b'], threshold_blocksize=5, copy_text='v')
	info_tables = camelot.read_pdf(pdf, flavor='stream', pages='2', row_tol=15,strip_text='\n', column_tol=15, table_areas=['0,650,540,540'])
	
	fn = "_posts/%s.html" % pcn_id
	if os.path.exists(fn):
		os.remove(fn)

	with open(fn, 'w') as f:
		info_tables[0].df.to_html(buf=f, header=False, index=False)
		with open(pdf, "rb") as pdf_f:
			pdf_text = pdftotext.PDF(pdf_f)
			first_page = pdf_text[1]
			if first_page.find('Description of Change'):
				write_html(f, first_page[first_page.find('Description of Change'):])
			for t in tables:
				t.df.to_html(buf=f, header=False, index=False)
				f.write("\n\n")
			second_page = pdf_text[2]
			if second_page.find('PCN Revision History'):
				write_html(f, first_page[first_page.find('PCN Revision History'):])
		
if __name__ == '__main__':
	if(len(sys.argv) > 1):
		parse_pdf(sys.argv[1])
	else:
		for pdf in glob.glob("pdf/*.pdf"):
			parse_pdf(pdf)