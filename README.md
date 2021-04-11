# SocialAutomation
This repository contains files relating to social automation tools.
Current Tools Include:
- Keyword engine originally designed for automating and cleaning up facebook posts moderating to a Facebook group however may be further developed for usage with other 
  string content management applications such as email, form data, or machine learning.
- Personal branding motivational / quote generator. Which may be used to generate thousands of images which may be used as inspitational posts.
  Ultimately generates content for regular posting.
  
Slogan maker contains Main which is parameterisable, MultiThread is purely an optimized solution allowing multiples images to be generate concurrently, provides an estimated 20-40% improvement in file generation speed assuming run is longer than 100 images.
usage: main.py [-h] [--quotepath [QUOTEPATH]] [--MultiThread [MULTITHREAD]]

optional arguments:
  -h, --help            show this help message and exit
  --quotepath [QUOTEPATH]
                        Path to the Quote File Path.
  --MultiThread [MULTITHREAD]
                        0=Single Threaded, 1=MultiThread
                        
