import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import json

class scrape:
    headerAgent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    flipkart_data=[]
    amazon_data=[]
    CREDS={}
    def __init__(self, parameter):
        f=open("creds.json")
        self.CREDS=json.load(f)
        self.flipkart(parameter)
        self.amazon(parameter)

    def flipkart(self,parameter):
        product='+'.join(parameter.split(' '))
        for i in range(1,21):
            url=f'https://www.flipkart.com/search?q={product}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}'
            try:
                response=requests.get(url,headers=self.headerAgent)
                soup=BeautifulSoup(response.text)
                cont=soup.find('div',class_=self.CREDS['flipkart_outerpage']['container_class'])
                prods=cont.find_all('div',class_=self.CREDS['flipkart_outerpage']['products_class'])
                for p in prods:
                    prod_links=p.find_all('a',class_=self.CREDS['flipkart_outerpage']['prod_link_class'])
                    img=p.find_all('img',self.CREDS['flipkart_outerpage']['image_class'])
                    for j in range(4):
                        data=[img[j]['src']]
                        data.append(self.CREDS['flipkart_outerpage']['base_url']+prod_links[j]['href'])
                        data.extend(self.extract_inside_data_flipkart(self.CREDS['flipkart_outerpage']['base_url']+prod_links[j]['href']))
                        self.flipkart_data.append(data)
                        data=[]
            except Exception as e:
                pass

    def amazon(self,parameter):
        product='+'.join(parameter.split(' '))
        for i in range(1,21):
            url=f'https://www.amazon.in/s?k={product}&page={i}&crid=1CXEZZ63ZDF8K&qid=1686048492&sprefix={product}%2Caps%2C244&ref=sr_pg_{i}'
            try:
                response=requests.get(url,headers=self.headerAgent)
                soup=BeautifulSoup(response.text,"html.parser")
                cont=soup.find('div',class_=self.CREDS['amazon_outerpage']['container_class'])
                img=cont.find_all('div',self.CREDS['amazon_outerpage']['image_id'])
                for j in img:
                    url=j.find('a',class_=self.CREDS['amazon_outerpage']['link_id'])
                    data=[j.find('img')['src']]
                    data.append(self.CREDS['amazon_outerpage']['base_url']+url['href'])
                    data.extend(self.extract_inside_data_amazon(self.CREDS['amazon_outerpage']['base_url']+url['href']))
                    self.amazon_data.append(data)
                    data=[]
            except Exception as e:
                pass

    def extract_inside_data_flipkart(self,url):
        try:
            response=requests.get(url,headers=self.headerAgent)
            soup=BeautifulSoup(response.text)
            prod_title=soup.find(self.CREDS['flipkart_innerpage']['title_tag_class'][0],class_=self.CREDS['flipkart_innerpage']['title_tag_class'][1]).text
            prod_price=soup.find(self.CREDS['flipkart_innerpage']['price_tag_class'][0],class_=self.CREDS['flipkart_innerpage']['price_tag_class'][1]).text
            rating=soup.find(self.CREDS['flipkart_innerpage']['rating_tag_class'][0],class_=self.CREDS['flipkart_innerpage']['rating_tag_class'][1]).text
            num_of_rating_and_reviews=soup.find(self.CREDS['flipkart_innerpage']['num_of_reviews_tag_class'][0],class_=self.CREDS['flipkart_innerpage']['num_of_reviews_tag_class'][1]).find('span').text
            prod_details=soup.find(self.CREDS['flipkart_innerpage']['prod_details_tag_class'][0],class_=self.CREDS['flipkart_innerpage']['prod_details_tag_class'][1]).find_all('div')
            details=[]
            n=0
            for p_d in prod_details:
                if n%3==0:
                    n+=1
                    continue
                if n%3==2:
                    details.append(p_d.text)
                    details.append(',')
                else:
                    details.append(p_d.text)
                n+=1
            
        except Exception as e:
            pass
        return [prod_title,prod_price,rating,num_of_rating_and_reviews,' '.join(details)]
    

    def extract_inside_data_amazon(self,url):
        try:
            response=requests.get(url,headers=self.headerAgent)
            soup=BeautifulSoup(response.text,"html.parser")
            prod_title=soup.find(self.CREDS['amazon_innerpage']['title_tag_class'][0],class_=self.CREDS['amazon_innerpage']['title_tag_class'][1]).text.strip()
            prod_price=soup.find(self.CREDS['amazon_innerpage']['price_tag_class'][0],class_=self.CREDS['amazon_innerpage']['price_tag_class'][1]).text.strip()
            try:
                rating=soup.find(self.CREDS['amazon_innerpage']['rating_tag_class'][0],class_=self.CREDS['amazon_innerpage']['rating_tag_class'][1]).text.strip()
            except Exception as e:
                rating=None
            try:
                num_of_rating_and_reviews=soup.find(self.CREDS['amazon_innerpage']['num_of_reviews_tag_class'][0],id=self.CREDS['amazon_innerpage']['num_of_reviews_tag_class'][1]).text.strip()
            except Exception as e:
                num_of_rating_and_reviews=None
            prod_details=soup.find(self.CREDS['amazon_innerpage']['prod_details_tag_class'][0],class_=self.CREDS['amazon_innerpage']['prod_details_tag_class'][1]).find_all('li')
            details=[]
            for p_d in prod_details:
                details.append(p_d.text.strip())
            
        except Exception as e:
            print(url)
        return [prod_title,prod_price,rating,num_of_rating_and_reviews,' '.join(details)]
    
s=scrape('shirts')
df1=pd.DataFrame(s.flipkart_data,columns=['Image URL','Product URL','Product Title','Product Price','ratings','number of reviews','product details'])
print(df1.head())
df1.to_csv('flipkart_data.csv')
df2=pd.DataFrame(s.amazon_data,columns=['Image URL','Product URL','Product Title','Product Price','ratings','number of reviews','product details'])
df2.to_csv('amazon_data.csv')