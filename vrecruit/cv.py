import PyPDF2
import textract
import re
import string
import pandas as pd
import matplotlib.pyplot as plt

def cv_screen():
    pdfFileObj = open('C:/Users/nikhi/Desktop/nik/Projects/vRecruit/Version 3/vrecruit/Resume --Rohini Prakash.pdf','rb')
    
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    
    num_pages = pdfReader.numPages
    
    count = 0
    
    text = ""
    
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count +=1
        text += pageObj.extractText()
    
    text = text.lower()
    
    text = re.sub(r'\d+','',text)
    
    text = text.translate(str.maketrans('','',string.punctuation))
    
    terms = {'Quality/Six Sigma':['black belt','capability analysis','control charts','doe','dmaic','fishbone',
                                  'gage r&r', 'green belt','ishikawa','iso','kaizen','kpi','lean','metrics',
                                  'pdsa','performance improvement','process improvement','quality',
                                  'quality circles','quality tools','root cause','six sigma',
                                  'stability analysis','statistical analysis','tqm'],      
            'Operations management':['automation','bottleneck','constraints','cycle time','efficiency','fmea',
                                     'machinery','maintenance','manufacture','line balancing','oee','operations',
                                     'operations research','optimization','overall equipment effectiveness',
                                     'pfmea','process','process mapping','production','resources','safety',
                                     'stoppage','value stream mapping','utilization'],
            'Supply chain':['abc analysis','apics','customer','customs','delivery','distribution','eoq','epq',
                            'fleet','forecast','inventory','logistic','materials','outsourcing','procurement',
                            'reorder point','rout','safety stock','scheduling','shipping','stock','suppliers',
                            'third party logistics','transport','transportation','traffic','supply chain',
                            'vendor','warehouse','wip','work in progress'],
            'Project management':['administration','agile','budget','cost','direction','feasibility analysis',
                                  'finance','kanban','leader','leadership','management','milestones','planning',
                                  'pmi','pmp','problem','project','risk','schedule','scrum','stakeholders'],
            'Data analytics':['analytics','api','aws','big data','busines intelligence','clustering','code',
                              'coding','data','database','data mining','data science','deep learning','hadoop',
                              'hypothesis test','iot','internet','machine learning','modeling','nosql','nlp',
                              'predictive','programming','python','r','sql','tableau','text mining',
                              'visualuzation'],
            'Healthcare':['adverse events','care','clinic','cphq','ergonomics','healthcare',
                          'health care','health','hospital','human factors','medical','near misses',
                          'patient','reporting system']}
    
    quality = 0
    operations = 0
    supplychain = 0
    project = 0
    data = 0
    healthcare = 0
    
    scores = []
    
    for area in terms.keys():
            
        if area == 'Quality/Six Sigma':
            for word in terms[area]:
                if word in text:
                    quality +=1
            scores.append(quality)
            
        elif area == 'Operations management':
            for word in terms[area]:
                if word in text:
                    operations +=1
            scores.append(operations)
            
        elif area == 'Supply chain':
            for word in terms[area]:
                if word in text:
                    supplychain +=1
            scores.append(supplychain)
            
        elif area == 'Project management':
            for word in terms[area]:
                if word in text:
                    project +=1
            scores.append(project)
            
        elif area == 'Data analytics':
            for word in terms[area]:
                if word in text:
                    data +=1
            scores.append(data)
            
        else:
            for word in terms[area]:
                if word in text:
                    healthcare +=1
            scores.append(healthcare)
    
    summary = pd.DataFrame(scores,index=terms.keys(),columns=['score']).sort_values(by='score',ascending=False)
    
    pie = plt.figure(figsize=(10,10))
    plt.pie(summary['score'], labels=summary.index, explode = (0.1,0,0,0,0,0), autopct='%1.0f%%',shadow=True,startangle=90)
    plt.title('Industrial Engineering Candidate - Resume Decomposition by Areas')
    plt.axis('equal')
    #plt.show()
    
    pie.savefig('resume_screening_results.png')