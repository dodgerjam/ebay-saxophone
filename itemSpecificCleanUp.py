import boto3
import pandas as pd
import logging
import numpy as np
import re


specifics = pd.read_csv('SaxophoneSpecifics.csv', 
delimiter = '\t', 
error_bad_lines=False, 
warn_bad_lines=False).groupby('Name')['Value'].unique()

def cleanUpType(saxtype):
    if saxtype in specifics['Type']:
        return saxtype

    if saxtype == saxtype:
        logging.info(saxtype)

    l_saxtype  = ' '+str(saxtype).lower()+' '
    if 'alto' in l_saxtype:
        logging.info(f'Mapping "{saxtype}" to "Alto"')
        return 'Alto'
    if 'tenor' in l_saxtype:
        logging.info(f'Mapping "{saxtype}" to "Tenor"')
        return 'Tenor'
    if 'soprano' in l_saxtype:
        logging.info(f'Mapping "{saxtype}" to "Soprano"')
        return 'Soprano'
    if 'bass' in l_saxtype or 'baritone' in l_saxtype:
        logging.info(f'Mapping "{saxtype}" to "Baritone/Bass"')
        return 'Baritone/Bass'
    if ' c ' in l_saxtype:
        logging.info(f'Mapping "{saxtype}" to "C Melody"')
        return 'C Melody'
    if 'sopranino' in l_saxtype:
        logging.info(f'Mapping "{saxtype}" to "C Melody"')
        return 'Sopranino'
    if 'plastic' in l_saxtype:
        logging.info(f'Mapping "{saxtype}" to "C Melody"')
        return 'Plastic'
    else:
        return np.nan

condition_dict = {1000:'New',
1500:'New other',
1750:'New with defects',
2000:'Manufacturer refurbished',
2500:'Seller refurbished',
2750:'Like New',
3000:'Used',
4000:'Very Good',
5000:'Good',
6000:'Acceptable',
7000:'For parts or not working'}

def cleanUpCondition(x):
    if x == x:
        return condition_dict[x]
    else:
        return x

sax_brands = ['P. Mauriat', 'Dakota', 'Antigua', 'Buescher', 'Vito', 'Amati', 'Armstrong', 'B&S', 'Berg Larsen', 'Boosey & Co', 'Buescher','Buffet', 'Buffet Crampon', 'Bundy', 'Cannonball', 'Conn', 'Elkhart', 'Gemeinhardt', 'Jupiter', 'Keilwerth', 'King', 'Martin', 'Odyssey', 'Selmer', 'Trevor James', 'Yamaha', 'Yanagisawa', 'Jean Baptiste']

def cleanUpBrand(brand):
    if brand != brand:
        return np.nan
    if brand.title() in sax_brands:
        return brand.title()
    brand = brand.title()

    intersect = set(brand.split(" ")).intersection(sax_brands)
    if len(intersect) == 1:
        logging.info(f'Mapping "{brand}" to "{list(intersect)[0]}"')
        return list(intersect)[0]
    if 'Conn' in brand:
        # logging.info(f'Mapping "{brand}" to "Conn"')
        return 'Conn'
    if 'unbranded' in brand.lower():
        # logging.info(f'Mapping "{brand}" to "Unbranded"')
        return 'Other'
    if 'selmer' in brand.lower():
        return 'Selmer'
    else:
        return 'Other'

def cleanUpSkill(skill):
    if skill in specifics['Skill Level']:
        return skill
    if not isinstance(skill, str):
        logging.info(skill)
    skill = skill.title()
    if 'Beginner' in skill and 'Intermediate' in skill:
        logging.info(f'Mapping "{skill}" to "Beginner/Intermediate"')
        return 'Beginner/Intermediate'
    
    undefined = ['Any', 'Unspecified', 'All', 'Everyone']
    for term in undefined:
        if term in skill:
            logging.info(f'Mapping "{skill}" to "Nan"')
            return 'Unspecified'
    
    if 'Biginer' in skill:
        logging.info(f'Mapping "{skill}" to "Beginner"')
        return 'Beginner'

    if 'Profesional' in skill:
        logging.info(f'Mapping "{skill}" to "Professional"')
        return 'Professional'

    return np.nan

def extractSkillFromModel(df):
    '''
    Requires Model column

    '''
    model_skill_dict = df.groupby(['Model'])['ItemSpecifics-Skill Level'].agg(lambda x: x.value_counts().index[0] if len(x.value_counts())>0 else np.nan).to_dict()
    return df['Model'].apply(lambda x: model_skill_dict[x] if x in model_skill_dict.keys() else np.nan)

def extractBrandFromTitle(title):

    possible_values = [x for x in sax_brands if x in title.title()]

    if len(possible_values) == 1:
        return possible_values[0]
    if len(possible_values) > 1:
        # Remove Issues Like Selmer Bundy, Buffet Crampon and Conn Elkhart
        possible_values = [x for x in possible_values if x not in ['Buffet', 'Selmer', 'Conn']]
        if len(possible_values) == 1:
            return possible_values[0]

    return np.nan

def extractTypeFromTitle(title):

    possible_values = [x for x in specifics['Type'] if x in title.title()]

    if len(possible_values) == 1:
        return possible_values[0]

    return np.nan

def yamahaModel(string):
    str1 = string.upper()
    if 'YSS' in str1:
        index = str1.index('YSS')
    elif 'YAS' in str1:
        index = str1.index('YAS')
    elif 'YTS' in str1:
        index = str1.index('YTS')
    elif 'YBS' in str1:
        index = str1.index('YBS')
    else:
        logging.info('WRONG MODEL TYPE SELECTED')
        return np.nan
        
    i = 1
    # find start of numbers
    while not str1[index + 3 +i].isdigit() and index + 3 +i < len(str1):
        i+=1
    j = 0
    index1 = index + i + 3
    while  index1 + j < len(str1):
        if not str1[index1+j].isdigit():
            break
        j+=1
    return re.sub(r'\W+', '', str1[index: index1 + j])

selmer_models = ['51J', '51JBL', '51JS', 'HENRI-SELMER-PARIS-52AXOS-ALTO-SAXOPHONE',
       '52JBL', '52JGP', '52JM', '52JS', '52JU', '53J', '53JA', '53JBL',
       '53JGP', '53JM', '53JS', '54JBL', '54JGP', '54JM', '54JS', '54JU',
       '55AFJ', '55AFJBL', '55AFJM', '55AFJS', '56', '62J', '62JA',
       '62JBL', '62JGP', '62JM', '62JS', '64J', '64JA', '64JBL', '64JGP',
       '64JM', '64JS', '66AFJ', '66AFJBL', '66AFJM', '72', '72F', '74',
       '74F', '84', '84F', 'AS400', 'AS42', 'AS42B', 'AS42S', 'AS42UL',
       'AS600-ALTO-SAXOPHONE', 'AS711', 'AWO1', 'AWO10', 'AWO10S',
       'AW010UL', 'AWO1S', 'AWO1UL', 'AWO2', 'AWO20', 'AWO20PG',
       'AWO20UL', 'AWO37', 'AWO37PG-YANAGISAWA-ALTO-SAXOPHONE', 'BS400',
       'BS500', 'BWO1', 'BWO10', 'BWO2', 'BWO20', 'BWO30BSB', 'CAS42WDIR',
       'SAS280R', 'SAS280RB', 'SAS280RC', 'SAS280RS', 'SBS280R', 'SCWO10',
       'SCWO20', 'SCWO37', 'SERIES-II-50J-HENRI-SELMER-PARIS-SAXOPHONE',
       'SSS280R', 'STS280R', 'STS280RB', 'STS280RC', 'STS280RS',
       'SWO1-YANAGISAWA-SOPRANO-SAXOPHONE',
       'SWO10-YANAGISAWA-SOPRANO-SAXOPHONE',
       'SWO2-YANAGISAWA-SOPRANO-SAXOPHONE',
       'SWO20-YANAGISAWA-SOPRANO-SAXOPHONE',
       'SWO3-YANAGISAWA-SOPRANO-SAXOPHONE',
       'SWO37-YANAGISAWA-SOPRANO-SAXOPHONE', 'TS400', 'TS44',
       'TS600-SAXOPHONE', 'TS711', 'TWO1',
       'TWO10-YANAGISAWA-TENOR-SAXOPHONE',
       'TWO10S-YANAGISAWA-TENOR-SAXOPHONE',
       'TWO2-YANAGISAWA-TENOR-SAXOPHONE',
       'TWO20-YANAGISAWA-TENOR-SAXOPHONE',
       'TWO20PG-YANAGISAWA-TENOR-SAXOPHONE',
       'TWO20UL-YANAGISAWA-TENOR-SAXOPHONE',
       'TWO37-YANAGISAWA-TENOR-SAXOPHONE', 'AS300', 'AS400', 'AS500',
       'AS600', 'BUNDY II']

def selmerModel(string):
    if 'Super Action 80' in string.title() or 'SA80' in string.upper().strip():
        if 'III' in string.upper():
            return 'Super Action 80 III' or '3 ' in string.upper()
        if 'II' in string.upper() or '2 ' in string.upper():
            return 'Super Action 80 II'
        return 'Super Action 80'

    if 'Super Balanced Action' in string.title():
        return 'Super Balanced Action'
    
    if 'mark' in string.lower() or ' mk' in string.lower():
        if 'vii' in string.lower() or '7 ' in string:
            return 'Mark VII'
        if 'vi' in string.lower() or '6 ' in string:
            return 'Mark VI'
        

    possible_values = [x for x in selmer_models if x in string.upper().strip()]

    if len(possible_values) == 1:
        return possible_values[0]
    
    if len(possible_values) > 1:
        return max(possible_values, key=len)

    return np.nan 

yanagisawa_models = ['SN981', 'SN9930', 'SCWO10', 'SCWO10U', 'SCWO10S', 'SCWO20',
       'SCWO20S', 'SCWO20U', 'SCWO37', 'SWO1', 'SWO1U', 'SWO1S', 'SWO2',
       'SWO2U', 'SWO10', 'SWO20', 'SWO20U', 'SWO3', 'SWO37', 'AWO1',
       'AWO1U', 'AWO2 ', 'AWO10', 'AWO10U', 'AWO20', 'AWO20U', 'AWO30',
       'AWO33', 'AWO32', 'AWO37', 'AWO20PG', 'TWO1', 'TWO1U', 'TWO2 ',
       'TWO10', 'TWO10U', 'TWO20', 'TWO20U', 'TWO30', 'TWO33', 'TWO32',
       'TWO20PG', 'TWO37', 'BWO10SKG', 'BWO1', 'BWO2', 'BWO10', 'BWO20',
       'BWO20U', 'BWO30BSB', 'S992PG', 'A901', 'A901U', 'T901', 'T901U',
       'A901B', 'A901S', 'A991', 'A902', 'A991U', 'S901', 'S901U',
       'SC991', 'SC991U', 'T991', 'T991U', 'T902', 'T901B', 'T901S',
       'SC991B', 'A991B', 'A991S', 'S991', 'S902', 'S902U', 'A992',
       'A992U', 'SC992', 'SC992U', 'T991B', 'T991S', 'T992', 'T992UL',
       'A9933', 'A9930', 'S992', 'SC9930', 'B901', 'T9930', 'T9933',
       'A9932J', 'S9030', 'A992PG', 'B902', 'S9930', 'B901B', 'B991',
       'T9932J', 'A900', 'T4', 'T5' 'T50', 'S6']

def yanagisawaModel(string):

    possible_values = [x for x in yanagisawa_models if x in string.upper().strip().replace('-','')]

    if len(possible_values) == 1:
        return possible_values[0]
    
    if len(possible_values) > 1:
        return max(possible_values, key=len)

    return np.nan





if __name__ == "__main__":
    s3 = boto3.client('s3')
    s3.list_objects(Bucket = 'ebayfindingdata', Prefix = 'shopping/')

    keys = [o['Key'] for o in s3.list_objects(Bucket = 'ebayfindingdata', Prefix = 'shopping')['Contents'] if '.csv' in o['Key']]
    df = pd.concat([pd.read_csv(s3.get_object(Bucket = 'ebayfindingdata', Key = k)['Body']) for k in keys])

    print(df[~df['ItemSpecifics-Type'].isna()]['ItemSpecifics-Type'].apply(cleanUpType).value_counts())
    print(df[~df['ItemSpecifics-Brand'].isna()]['ItemSpecifics-Brand'].apply(cleanUpBrand).value_counts())
    print(df[~df['ItemSpecifics-Skill Level'].isna()]['ItemSpecifics-Skill Level'].apply(cleanUpSkill).value_counts())