
from scrapy import Spider
from drugreview.items import DrugreviewItem
import requests
from scrapy.http import TextResponse
import unicodedata
import numpy as np
import pandas as pd
from scrapy.selector import Selector
import re

class DrugreviewSpider(Spider):
    name = 'drug_spider.py'
    allowed_urls = ['www.drugs.com']
    start_urls = ['https://www.drugs.com/alpha/a.html']

    def parse(self,response):

        TAG_RE = re.compile(r'<[^>]+>')
        def remove_tags(text):
            return TAG_RE.sub('',text)

        def first_one(N):
            ct = 0
            for p in range(0,len(N)):
                if N[p]==0:
                    ct = ct+1
                else:
                    break
            return ct

        item = DrugreviewItem()

        alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        Letters = 26
        for i in range(0,Letters):
            url_drug = 'https://www.drugs.com/alpha/'+str(alphabet[i])+'.html'
            r = requests.get(url_drug)
            response = TextResponse(r.url,body=r.text,encoding='utf-8')
            rows = response.xpath('//*[@id="content"]/div[2]/ul/li/a/text()').extract()
            rowlink = response.xpath('//*[@id="content"]/div[2]/ul/li/a/@href').extract()

            for row in range(0,len(rows)):

                Drug_Name = rows[row]
                url_1 = 'https://www.drugs.com'+unicodedata.normalize('NFKD',rowlink[row]).encode('ascii','ignore')
                r = requests.get(url_1)
                response_1 = TextResponse(r.url,body=r.text,encoding='utf-8')
                nrows = response_1.xpath('//*[@id="moreResources"]/ul[1]/li/a/text()').extract()
                nrows_links = response_1.xpath('//*[@id="moreResources"]/ul[1]/li/a/@href').extract()
              
                #Assign all Fields to "item"
                item['Drug_Name'] = Drug_Name

                #Assign "Drug_Class" to "item"
                k = [j for j in range(0,len(nrows)) if nrows[j].find("Drug class")>=0]
                if len(k)==0:
                    item['Drug_Class'] = 'NA'
                else:
                    m = k[0]
                    Drug_Class = unicodedata.normalize('NFKD',nrows[m].split(': ')[1]).encode('ascii','ignore')
                    item['Drug_Class'] = Drug_Class

                #Assign "FDA_Alerts" to "item"
                k = [j for j in range(0,len(nrows)) if nrows[j].find("FDA Alerts")>=0]
                if len(k)==0:
                    item['FDA_Alerts'] = 'NA'
                else:
                    m = k[0]
                    FDA_Alerts = unicodedata.normalize('NFKD',nrows[m].split()[2].split('(')[1].split(')')[0]).encode('ascii','ignore')
                    item['FDA_Alerts'] = FDA_Alerts

                #Assign "Drug_Interactions" to "item"
                k = [j for j in range(0,len(nrows)) if nrows[j].find("Interactions")>=0]
                if len(k)==0:
                    item['Drug_Interactions'] = 'NA'
                else:
                    m = k[0]
                    url_2 = 'https://www.drugs.com'+unicodedata.normalize('NFKD',nrows_links[m]).encode('ascii','ignore')
                    r = requests.get(url_2)
                    response_2 = TextResponse(r.url,body=r.text,encoding='utf-8')
                    Drug_Interactions = response_2.xpath('//*[@id="content"]/div[2]/ul[1]/li/b/text()').extract()
                    item['Drug_Interactions'] = Drug_Interactions

                #Assign "NReviews" to "item"
                k1 = [j for j in range(0,len(nrows)) if nrows[j].find("Review")>=0]
                if len(k1)==0:
                    item['NReviews'] = 'NA'                    
                else:
                    m = k1[0]
                    NPages = int(np.ceil(float(nrows[m].split()[0])/25.))
                    Condition = list()
                    Comment = list()
                    UserRating = list()
                    Date = list()
                    Duration = list()
                    
                    NC=[0]*NPages

                    for ind_page in range(0,NPages):
                        indurl = 'https://www.drugs.com'+unicodedata.normalize('NFKD',nrows_links[m]).encode('ascii','ignore')+'?page='+str(ind_page+1)
                        r = requests.get(indurl)
                        response = TextResponse(r.url,body=r.text,encoding='utf-8')
                        NC[ind_page] = len(response.xpath('//*[@id="content"]/div[2]/div/div/div/p[1]/span/text()').extract())

                    NReviews_cnt = sum(NC)
                    CNumber = 0

                    for ind_page in range(0,NPages):
                        indurl = 'https://www.drugs.com'+unicodedata.normalize('NFKD',nrows_links[m]).encode('ascii','ignore')+'?page='+str(ind_page+1)              
                        r = requests.get(indurl)
                        response = TextResponse(r.url,body=r.text,encoding='utf-8')
                        NComments = len(response.xpath('//*[@id="content"]/div[2]/div/div/div/p[1]/span/text()').extract())
                        check_comment_present = [0]*len(range(0,10))

                        for z in range(0,10):
                            check_comment_present[z] = len(response.xpath('//*[@id="content"]/div[2]/div['+str(z)+']/div/div/p[1]/span/text()').extract())
                        n_cnt = first_one(check_comment_present)
                        
                        for n in range(0,NComments):
                            cnt = n+n_cnt
                            CNumber = CNumber+1

                            #Calculate "Comment"
                            Comment_Ind = response.xpath('//*[@id="content"]/div[2]/div['+str(cnt)+']/div/div/p[1]/span/text()').extract()
                            if len(Comment_Ind) == 0:
                                Comment_Ind = "NA"
                            Comment = Comment_Ind

                            #Calculate "Condition"
                            Condition_Ind = response.xpath('//*[@id="content"]/div[2]/div['+str(cnt)+']/div/div/p[1]/b/text()').extract()
                            if len(Condition_Ind)==0:
                                Condition_Ind = 'NA'
                            Condition = Condition_Ind

                            #Calculate "UserRating"
                            UserRating_Ind = response.xpath('//*[@id="content"]/div[2]/div').extract()
                            UserRating_Ind1 = Selector(text=UserRating_Ind[cnt-1]).xpath('//td/div/text()').extract()
                            if len(UserRating_Ind1)==0:
                                UserRating = 'NA'
                            else:
                                UserRating = float(UserRating_Ind1[3])

                            #Calculate "Useful_Reviews"
                            Useful_Reviews_Ind = response.xpath('//*[@id="content"]/div[2]/div').extract()[cnt-1]
                            Useful_Reviews_List = list(unicodedata.normalize('NFKD',Useful_Reviews_Ind).encode('ascii','ignore').split())
                            k = [j for j in range(0,len(Useful_Reviews_List)) if Useful_Reviews_List[j]=="users"]
                            if len(k)==0:
                                Useful_Reviews = 'NA'
                            else:
                                Useful_Reviews = str((remove_tags(Useful_Reviews_List[k[0]-1])))

                            #Calculate "Duration"
                            l = len(response.xpath('//*[@id="content"]/div[2]/div['+str(cnt)+']/div/div/p[2]/span/text()').extract())
                            Date_Ind = response.xpath('//*[@id="content"]/div[2]/div['+str(cnt)+']/div/div/p[2]/span['+str(l)+']/text()').extract()
                            if l==2:
                                Duration_Ind = response.xpath('//*[@id="content"]/div[2]/div['+str(cnt)+']/div/div/p[2]/span[1]/text()').extract()
                            else:
                                Duration_Ind = 'NA'
                            Duration = Duration_Ind

                            #Calculate "Date"
                            if len(Date_Ind)==0:
                                Date_Ind = 'NA'
                            Date = Date_Ind
                            
                            #Assign the Fields to "item"
                            item['Condition'] = Condition
                            item['Comment'] = Comment
                            item['Date'] = Date
                            item['Duration'] = Duration
                            item['NReviews'] = NReviews_cnt
                            item['UserRating'] = UserRating
                            item['Useful_Reviews'] = Useful_Reviews
                            # item['CNumber'] = [CNumber,i,row,ind_page,n]

                            yield item