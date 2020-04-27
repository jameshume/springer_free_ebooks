import pandas as pd
from tabula import read_pdf
from bs4 import BeautifulSoup
import requests
import re
import sys
import os

try:
	os.makedirs('springerbooks')
except FileExistsError as ex:
	print("### WARNING springerbooks already exists")
	pass


df_list = read_pdf('freebooks.pdf', pages='all')

# First line of first frame is table titles, loose it
df_list[0] = df_list[0].drop(df_list[0].index[0])

for page_no, df in enumerate(df_list):
	for index, row in df.iterrows():
		print("Getting ", row[1], "from page", page_no)
		try:
			html_page = requests.get(row[4])
			soup = BeautifulSoup(html_page.text, 'html.parser')
			links = set()
			for link in soup.findAll('a', attrs={'title': re.compile("^Download this book")}):
				links.add(link.get('href'))
			
			if len(links) != 0:
				if len(links) > 1: print('### WARNING TOO MANY LINKS. CHECK THIS.')
				pdf_url = 'https://link.springer.com{}'.format(links.pop())
				print("   - Downloading from", pdf_url)
				pdf = requests.get(pdf_url)
				with open('springerbooks/{}.pdf'.format(row[1].replace(" ", "_")), 'wb') as f:
					f.write(pdf.content)
			else:
				print("### FAILED TO PARSE LINK FOR {}:{}".format(row[0], row[1]))
		except Exception as e:
			print("### FAILED for ", row[1], e)
			sys.exit(1)
