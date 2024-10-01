from .webservice import WebService
from datetime import datetime
from json import dumps

class Sync:
    def __init__(self, host, user, token):
        self.ws = WebService(host)
        self.user_id = self.ws.doLogin(user, token)['userId'] 
        salesOrderDescribe = self.ws.doDescribe('Contacts')
        print(self.user_id)
    
    def search(self, module, condition):
        condition_sql = " AND ".join([f"{key} = '{value}'" for key, value in condition.items()])
        i = 0
        result = []
        while(True):
            query_request = f"SELECT * FROM {module} WHERE {condition_sql} LIMIT {i}, {i + 100}"
            print(query_request)
            query_result = self.ws.doQuery(query_request)
            i += 100
            result.extend(query_result)
            if len(query_result) < 100:
                break
        
        return result
            
            
    def get_contact_id(self, firstname, lastname, dob):
        # contact_exist = self.ws.doQuery(f"SELECT id FROM Contacts WHERE firstname = '{firstname}' AND lastname = '{lastname}' AND cf_790 = '{datetime.strptime(dob, '%m-%d-%Y').strftime('%Y-%m-%d')}'")
        contact_exist = self.ws.doQuery(f"SELECT id FROM Contacts WHERE firstname = '{firstname}' AND lastname = '{lastname}'")
        return contact_exist[0]['id']
    
    def get_salesorder_id(self, subject):
        # contact_exist = self.ws.doQuery(f"SELECT id FROM Contacts WHERE firstname = '{firstname}' AND lastname = '{lastname}' AND cf_790 = '{datetime.strptime(dob, '%m-%d-%Y').strftime('%Y-%m-%d')}'")
        salesorder_exist = self.ws.doQuery(f"SELECT * FROM SalesOrder WHERE subject = '{subject}'")
        print(salesorder_exist)
        return salesorder_exist[0]['id']

    def create_contact(self, contact_data):
        contact_id = self.ws.doCreate('Contacts', contact_data)
        return contact_id['id']
        
    def create_salesorder(self, salesorder_data):
        salesOrder_id = self.ws.doCreate('SalesOrder', salesorder_data)
        return salesOrder_id['id']
        
        
    def create(self, basicInfo, dependentInfo, payInfo, helpDeskInfo, sellInfo):
        basicDict = basicInfo
        dependentDict = [item for item in dependentInfo]
        helpDeskDict = [item for item in helpDeskInfo]
        payDict = payInfo
        sellDict = sellInfo
        salesOrderDescribe = self.ws.doDescribe('SalesOrder')
        #contactDescribe = self.ws.doDescribe('Contacts')
        contactExist = self.ws.doQuery(f"SELECT id FROM Contacts WHERE firstname = '{basicDict.firstname['value']}' AND lastname = '{basicDict.lastname['value']}' AND cf_759 = '{datetime.strptime(basicDict.dob['value'], '%b %d %Y').strftime('%Y-%m-%d')}'")
        if len(contactExist) == 0:
            contactData = self.getContactData(basicDict, payDict)
            contactData = {key: value for key, value in contactData.items() if value != ''}
            contact = self.ws.doCreate('Contacts', contactData)
            if contact != False:
                if len(contact) > 0:
                    salesOrderData = self.getSalesOrderData(basicDict, dependentDict, payDict, contact['id'])
                    #salesOrderData = {key: value for key, value in salesOrderData.items() if value != ''}
                    salesOrder = self.ws.doCreate('SalesOrder', salesOrderData)
                    helpDeskDict.append({
                        'status': 'Open',
                        'title': 'INSCRIPCIÓN INICIAL',
                        'cf_2727': '2024',
                        'description': f"{datetime.now().strftime('%m/%d/%Y')} Mr. Rocky <3\n\n \
                            Familia: {payDict.family['value']}\n \
                            SSN: {basicDict.ssn['value']}\n \
                            Ingresos: ${payDict.income['value']}\n \
                            Prima Estimada: ${payDict.premium['value']}\n \
                            Compañía: {payDict.company['value']}\n \
                            {'Plan ID: ' + payDict.planid['value'] if payDict.planid['value'] != '' else 'MP ID: ' + payDict.mpid['value']}\n \
                            Broker: {basicDict.broker['value']}\n \
                            Efectividad: {datetime.strptime(f'{datetime.now().month + 1}/01/{datetime.now().year}', '%m/%d/%Y').strftime('%m/%d/%Y')}\n \
                            Prima: ${payDict.premium['value']}"
                    })
                    for helpDesk in helpDeskDict:
                        helpDeskData = self.getHelpDeskData(helpDesk, contact['id'], payDict.company['value'])
                        helpDesk = self.ws.doCreate('HelpDesk', helpDeskData)
                    #return "X ERROR")
                    return "ok"
        else:
            return f"Ya existe el self.wse {basicDict.firstname['value']} {basicDict.lastname['value']} con el código {contactExist[0]['id']}"
        
    def getHelpDeskData(self, helpDesk, contactID, company) -> dict:
        return {
            'assigned_user_id': '19x75',
            'ticketstatus': helpDesk['status'],
            'ticket_title': helpDesk['title'],
            'contact_id': contactID,
            'cf_1987': helpDesk['title'],
            'cf_2259': company,
            'cf_2727': self.getYear(datetime.now().strftime('%m/%d/%Y')),
            'description': helpDesk['description']
        }
        
    def getContactData(self, basicDict, payDict) -> dict:
        return {
            'cf_1979': self.getPeriod(False, datetime.strptime(basicDict.selldate['value'], '%b %d %Y').strftime('%Y-%m-%d')),
            'cf_2319': self.getYear(datetime.now().strftime('%m/%d/%Y')),
            'cf_801': 'SPANISH' if basicDict.language['value'] == 'Spanish' else 'ENGLISH',
            'firstname': basicDict.firstname['value'],
            'cf_1895': basicDict.middlename['value'],
            'lastname': basicDict.lastname['value'],
            'cf_763': basicDict.ssn['value'],
            'cf_759': datetime.strptime(basicDict.dob['value'], '%b %d %Y').strftime('%Y-%m-%d'),
            'cf_771': 'MALE' if basicDict.gender['value'] == 'Male' else 'FEMALE',
            'cf_1989': 'APLICA MP' if basicDict.coverage['label'] == 'Yes' else ('MEDICAID' if basicDict.coverage['label'] == 'Medicaid' else 'NO DESEA'),
            'cf_809': f"{basicDict.address['address']['value']} {basicDict.address['optional']['value']}",
            'cf_817': basicDict.address['city']['value'],
            'cf_825': basicDict.address['state']['value'],
            'cf_821': basicDict.address['zipcode']['value'],
            'cf_1923': basicDict.address['county']['value'],
            'cf_819': basicDict.phone1['value'],
            'cf_827': basicDict.phone2['value'],
            'cf_815': basicDict.email['value'],
            'cf_2003': basicDict.age['value'],
            'cf_755': basicDict.pob['value'],
            'cf_775': 'YES' if basicDict.smoke['value'] == 'Yes' else 'NOT',
            'cf_785': payDict.typeIncome['value'],
            'cf_787': 'YES' if basicDict.jail['value'] == 'Yes' else 'NOT',
            'cf_2103': basicDict.pregnant['value'],
            'cf_2253': payDict.income['value'],
            'cf_757': self.getDocument(basicDict.document['value']),
            'cf_2187': 'Nueva' if basicDict.coverage['label'] == 'Yes' else ('Autorización' if basicDict.coverage['label'] == 'Autorización' else 'Recuperada'),
            'cf_2767': 'SEND' if basicDict.aor['value'] == 'sent' else 'YES'
        }
        
    def getSalesOrderData(self, basicDict, dependentDict, payDict, contactID) -> dict:
        spouse =  [spouse for spouse in dependentDict if spouse['relationship']['value'] == 'Spouse'] if dependentDict else []
        dependent =  [dependent for dependent in dependentDict if dependent['relationship']['value'] != 'Spouse'] if dependentDict else []
        return {
            'subject': f"{basicDict.firstname['value']} {basicDict.lastname['value']}",
            'contact_id': contactID,
            'cf_2799': payDict.addressPay['value'],
            'cf_2255': datetime.now().strftime('%Y-%m-%d'),
            'cf_2257': 'Mr. Rocky',
            'cf_2179': datetime.strptime(basicDict.selldate['value'], '%b %d %Y').strftime('%Y-%m-%d'),
            'cf_2141': 'Sin digitar',
            'cf_1463': 'YES' if payDict.autopay['value'] == 'Yes' else 'NO',
            'cf_2147': payDict.autoPayDay['value'],
            'cf_2033': payDict.premium['value'],
            'cf_2067': 'Sin Broker' if basicDict.broker['value'] == 'Autorización' else basicDict.broker['value'],
            'cf_2069': payDict.company['value'],
            'cf_2035': payDict.planid['value'],
            'cf_2025': payDict.income['value'],
            'cf_2733': 'Negocio' if payDict.typeAccount['value'] == 'business' else 'Personal',
            'cf_2737': f"{basicDict.address['address']['value']} {basicDict.address['optional']['value']}",
            'cf_2739': basicDict.address['city']['value'],
            'cf_2765': basicDict.address['state']['value'],
            'cf_2743': basicDict.address['zipcode']['value'],
            'cf_2745': basicDict.address['county']['value'],
            'cf_2751': basicDict.phone1['value'],
            'cf_2747': basicDict.email['value'],
            'cf_2293': basicDict.firstname['value'],
            'cf_2295': basicDict.middlename['value'],
            'cf_2297': basicDict.lastname['value'],
            'cf_2321': basicDict.ssn['value'],
            'cf_2299': datetime.strptime(basicDict.dob['value'], '%b %d %Y').strftime('%Y-%m-%d'),
            'cf_2335': 'YES' if basicDict.smoke['value'] == 'Yes' else 'NOT',
            'cf_2333': 'YES' if basicDict.jail['value'] == 'Yes' else 'NOT',
            'cf_2303': basicDict.gender['value'],
            'cf_2291': basicDict.age['value'],
            'cf_2629': basicDict.pob['value'],
            'cf_2323': 'YES' if len(spouse) > 0 else 'NOT',
            'cf_2601': self.getDocument(basicDict.document['value']),
            'cf_2387': payDict.typeIncome['value'],
            'cf_1479': payDict.accountPay['value'],
            'cf_1483': payDict.accountPay['value'][-4:],
            'cf_2145': payDict.ownerPay['value'],
            'cf_1475': payDict.routePay['value'],
            'cf_1481': 'VISA' if payDict.cardPay['value'][:1] == '4' else ('MASTERCARD' if payDict.cardPay['value'][:1] == '5' else ('DISCOVERY' if payDict.cardPay['value'][:1] == '6' else ('AMERICAN EXPRESS' if payDict.cardPay['value'][:1] == '3' else ''))),
            'cf_1469': payDict.cardPay['value'][-4:],
            'cf_1465': payDict.cardPay['value'],
            'cf_1473': payDict.expirationPay['value'],
            'cf_1477': payDict.codePay['value'],
            'cf_1471': payDict.bankAccount['value'],
            'cf_2157': payDict.typeCard['value'],
            'cf_2797': payDict.typeAccount['value'],
            'cf_2059': datetime.strptime(f'{datetime.now().month + 1}/01/{datetime.now().year}', '%m/%d/%Y').strftime('%Y-%m-%d'),
            'cf_2193': f"{datetime.now().year}-12-31",
            'cf_2385': 'OBAMACARE' if basicDict.coverage['label'] == 'Yes' else ('MEDICAID' if basicDict.coverage['label'] == 'Medicaid' else 'NO APLICA'),
            'cf_2337': payDict.income['value'],
            'cf_2369': 'SPANISH' if basicDict.language['value'] == 'Spanish' else 'ENGLISH',
            'cf_2347': spouse[0]['firstname']['value'] if len(spouse) > 0 else '',
            'cf_2349': spouse[0]['middlename']['value'] if len(spouse) > 0 else '',
            'cf_2351': spouse[0]['lastname']['value'] if len(spouse) > 0 else '',
            'cf_2357': spouse[0]['ssn']['value'] if len(spouse) > 0 else '',
            'cf_2359': ('MALE' if spouse[0]['gender']['value'] == 'Male' else 'FEMALE') if len(spouse) > 0 else '',
            'cf_2355': datetime.strptime(spouse[0].dob['value'], '%b %d %Y').strftime('%Y-%m-%d') if len(spouse) > 0 else '',
            'cf_2631': spouse[0]['pob']['value']['value'] if len(spouse) > 0 else '',
            'cf_2709': '' if len(spouse) == 0 else ('YES' if spouse[0]['smoke']['value'] == 'Yes' else ('NOT' if spouse[0]['smoke']['value'] == 'No' else '')),
            'cf_2383': '' if len(spouse) == 0 else ('YES' if spouse[0]['pregnant']['value'] == 'Yes' else ('NOT' if spouse[0]['pregnant']['value'] == 'No' else '')),
            'cf_2603': '' if len(spouse) == 0 else self.getDocument(spouse[0]['document']['value']),
            'cf_2389': '' if len(spouse) == 0 else ('OBAMACARE' if len(spouse) > 0 and spouse[0]['coverage']['label'] == 'Yes' else ('MEDICAID' if len(spouse) > 0 and spouse[0]['coverage']['label'] == 'Medicaid' else None)),
            'cf_2405': dependent[0]['firstname']['value'] if len(dependent) >= 1 else '',
            'cf_2407': dependent[0]['middlename']['value'] if len(dependent) >= 1 else '',
            'cf_2409': dependent[0]['lastname']['value'] if len(dependent) >= 1 else '',
            'cf_2417': dependent[0]['ssn']['value'] if len(dependent) >= 1 else '',
            'cf_2413': datetime.strptime(dependent[0].dob['value'], '%b %d %Y').strftime('%Y-%m-%d') if len(dependent) >= 1 else '',
            'cf_2411': ('MALE' if dependent[0]['gender']['value'] == 'Male' else 'FEMALE') if len(dependent) >= 1 else '',
            'cf_2711': '' if len(dependent) == 0 else ('YES' if len(dependent) >= 1 and  dependent[0]['smoke']['value'] == 'Yes' else ('NOT' if len(dependent) >= 1 and  dependent[0]['smoke']['value'] == 'No' else '')),
            'cf_2423': '' if len(dependent) == 0 else ('YES' if len(dependent) >= 1 and  dependent[0]['pregnant']['value'] == 'Yes' else ('NOT' if len(dependent) >= 1 and  dependent[0]['pregnant']['value'] == 'No' else '')),
            'cf_2431': '' if len(dependent) == 0 else ('HIJO(A)' if len(dependent) >= 1 and  dependent[0]['relationship']['value'] == 'Son/Daughter' else ('ABUELO(A)' if len(dependent) >= 1 and  dependent[0]['relationship']['value'] == 'Grandparent' else ('PADRE/MADRE' if len(dependent) >= 1 and dependent[0]['document']['value'] == 'Parent' else ('HERMANO(A)' if len(dependent) >= 1 and dependent[0]['document']['value'] == 'Sibling' else ('NIETO(A)' if len(dependent) >= 1 and dependent[0]['document']['value'] == 'Grandchild' else ('SOBRINO(A)' if len(dependent) >= 1 and dependent[0]['document']['value'] == 'Nephew/Niece' else ('TIO(A)' if len(dependent) >= 1 and dependent[0]['document']['value'] == 'Aunt/Uncle' else ('CUÑADO(A)' if len(dependent) >= 1 and dependent[0]['document']['value'] == 'Brother/Sister in-law' else ('YERNO/NUERA' if len(dependent) >= 1 and dependent[0]['document']['value'] == 'Son/Daughter in-law' else ''))))))))),
            'cf_2401': '' if len(dependent) == 0 else ('OBAMACARE' if len(dependent) >= 1 and dependent[0]['coverage']['label'] == 'Yes' else ('MEDICAID' if len(dependent) >= 1 and dependent[0]['coverage']['label'] == 'Medicaid' else 'NO APLICA')),
            'cf_2605': '' if len(dependent) == 0 else self.getDocument(dependent[0]['document']['value']),
            'cf_2443': dependent[1]['firstname']['value'] if len(dependent) >= 2 else '',
            'cf_2445': dependent[1]['middlename']['value'] if len(dependent) >= 2 else '',
            'cf_2447': dependent[1]['lastname']['value'] if len(dependent) >= 2 else '',
            'cf_2455': dependent[1]['ssn']['value'] if len(dependent) >= 2 else '',
            'cf_2451': datetime.strptime(dependent[1].dob['value'], '%b %d %Y').strftime('%Y-%m-%d') if len(dependent) >= 2 else '',
            'cf_2449': ('MALE' if dependent[1]['gender']['value'] == 'Male' else 'FEMALE') if len(dependent) >= 2 else '',
            'cf_2713': '' if len(dependent) <= 1 else ('YES' if len(dependent) >= 2 and  dependent[1]['smoke']['value'] == 'Yes' else ('NOT' if len(dependent) >= 2 and  dependent[1]['smoke']['value'] == 'No' else '')),
            'cf_2459': '' if len(dependent) <= 1 else ('YES' if len(dependent) >= 2 and  dependent[1]['pregnant']['value'] == 'Yes' else ('NOT' if len(dependent) >= 2 and  dependent[1]['pregnant']['value'] == 'No' else '')),
            'cf_2465': '' if len(dependent) <= 1 else ('HIJO(A)' if len(dependent) >= 2 and  dependent[1]['relationship']['value'] == 'Son/Daughter' else ('ABUELO(A)' if len(dependent) >= 2 and  dependent[1]['relationship']['value'] == 'Grandparent' else ('PADRE/MADRE' if len(dependent) >= 2 and dependent[1]['document']['value'] == 'Parent' else ('HERMANO(A)' if len(dependent) >= 2 and dependent[1]['document']['value'] == 'Sibling' else ('NIETO(A)' if len(dependent) >= 2 and dependent[1]['document']['value'] == 'Grandchild' else ('SOBRINO(A)' if len(dependent) >= 2 and dependent[1]['document']['value'] == 'Nephew/Niece' else ('TIO(A)' if len(dependent) >= 2 and dependent[1]['document']['value'] == 'Aunt/Uncle' else ('CUÑADO(A)' if len(dependent) >= 2 and dependent[1]['document']['value'] == 'Brother/Sister in-law' else ('YERNO/NUERA' if len(dependent) >= 2 and dependent[1]['document']['value'] == 'Son/Daughter in-law' else ''))))))))),
            'cf_2439': '' if len(dependent) <= 1 else ('OBAMACARE' if len(dependent) >= 2 and dependent[1]['coverage']['label'] == 'Yes' else ('MEDICAID' if len(dependent) >= 2 and dependent[1]['coverage']['label'] == 'Medicaid' else 'NO APLICA')),
            'cf_2607': '' if len(dependent) <= 1 else self.getDocument(dependent[1]['document']['value']),
            'cf_2479': dependent[2]['firstname']['value'] if len(dependent) >= 3 else '',
            'cf_2481': dependent[2]['middlename']['value'] if len(dependent) >= 3 else '',
            'cf_2483': dependent[2]['lastname']['value'] if len(dependent) >= 3 else '',
            'cf_2491': dependent[2]['ssn']['value'] if len(dependent) >= 3 else '',
            'cf_2487': datetime.strptime(dependent[2].dob['value'], '%b %d %Y').strftime('%Y-%m-%d') if len(dependent) >= 3 else '',
            'cf_2485': ('MALE' if dependent[2]['gender']['value'] == 'Male' else 'FEMALE') if len(dependent) >= 3 else '',
            'cf_2715': '' if len(dependent) <= 2 else ('YES' if len(dependent) >= 3 and  dependent[2]['smoke']['value'] == 'Yes' else ('NOT' if len(dependent) >= 3 and  dependent[2]['smoke']['value'] == 'No' else '')),
            'cf_2495': '' if len(dependent) <= 2 else ('YES' if len(dependent) >=3 and  dependent[2]['pregnant']['value'] == 'Yes' else ('NOT' if len(dependent) >= 3 and  dependent[2]['pregnant']['value'] == 'No' else '')),
            'cf_2501': '' if len(dependent) <= 2 else ('HIJO(A)' if len(dependent) >= 3 and  dependent[2]['relationship']['value'] == 'Son/Daughter' else ('ABUELO(A)' if len(dependent) >= 3 and  dependent[2]['relationship']['value'] == 'Grandparent' else ('PADRE/MADRE' if len(dependent) >= 3 and dependent[2]['document']['value'] == 'Parent' else ('HERMANO(A)' if len(dependent) >= 3 and dependent[2]['document']['value'] == 'Sibling' else ('NIETO(A)' if len(dependent) >= 3 and dependent[2]['document']['value'] == 'Grandchild' else ('SOBRINO(A)' if len(dependent) >= 3 and dependent[2]['document']['value'] == 'Nephew/Niece' else ('TIO(A)' if len(dependent) >= 3 and dependent[2]['document']['value'] == 'Aunt/Uncle' else ('CUÑADO(A)' if len(dependent) >= 3 and dependent[2]['document']['value'] == 'Brother/Sister in-law' else ('YERNO/NUERA' if len(dependent) >= 3 and dependent[2]['document']['value'] == 'Son/Daughter in-law' else ''))))))))),
            'cf_2475': '' if len(dependent) <= 2 else ('OBAMACARE' if len(dependent) >= 3 and dependent[2]['coverage']['label'] == 'Yes' else ('MEDICAID' if len(dependent) >= 3 and dependent[2]['coverage']['label'] == 'Medicaid' else 'NO APLICA')),
            'cf_2609': '' if len(dependent) <= 2 else self.getDocument(dependent[2]['document']['value']),
            'cf_2515': dependent[3]['firstname']['value'] if len(dependent) >= 4 else '',
            'cf_2517': dependent[3]['middlename']['value'] if len(dependent) >= 4 else '',
            'cf_2519': dependent[3]['lastname']['value'] if len(dependent) >= 4 else '',
            'cf_2527': dependent[3]['ssn']['value'] if len(dependent) >= 4 else '',
            'cf_2523': datetime.strptime(dependent[3].dob['value'], '%b %d %Y').strftime('%Y-%m-%d') if len(dependent) >= 4 else '',
            'cf_2521': ('MALE' if dependent[3]['gender']['value'] == 'Male' else 'FEMALE') if len(dependent) >= 4 else '',
            'cf_2717': '' if len(dependent) <= 3 else ('YES' if len(dependent) >= 4 and  dependent[3]['smoke']['value'] == 'Yes' else ('NOT' if len(dependent) >= 4 and  dependent[3]['smoke']['value'] == 'No' else '')),
            'cf_2531': '' if len(dependent) <= 3 else ('YES' if len(dependent) >= 4 and  dependent[3]['pregnant']['value'] == 'Yes' else ('NOT' if len(dependent) >= 4 and  dependent[3]['pregnant']['value'] == 'No' else '')),
            'cf_2537': '' if len(dependent) <= 3 else ('HIJO(A)' if len(dependent) >= 4 and  dependent[3]['relationship']['value'] == 'Son/Daughter' else ('ABUELO(A)' if len(dependent) >= 4 and  dependent[3]['relationship']['value'] == 'Grandparent' else ('PADRE/MADRE' if len(dependent) >= 4 and dependent[3]['document']['value'] == 'Parent' else ('HERMANO(A)' if len(dependent) >= 4 and dependent[3]['document']['value'] == 'Sibling' else ('NIETO(A)' if len(dependent) >= 4 and dependent[3]['document']['value'] == 'Grandchild' else ('SOBRINO(A)' if len(dependent) >= 4 and dependent[3]['document']['value'] == 'Nephew/Niece' else ('TIO(A)' if len(dependent) >= 4 and dependent[3]['document']['value'] == 'Aunt/Uncle' else ('CUÑADO(A)' if len(dependent) >= 4 and dependent[3]['document']['value'] == 'Brother/Sister in-law' else ('YERNO/NUERA' if len(dependent) >= 4 and dependent[3]['document']['value'] == 'Son/Daughter in-law' else ''))))))))),
            'cf_2511': '' if len(dependent) <= 3 else ('OBAMACARE' if len(dependent) >= 4 and dependent[3]['coverage']['label'] == 'Yes' else ('MEDICAID' if len(dependent) >= 4 and dependent[3]['coverage']['label'] == 'Medicaid' else 'NO APLICA')),
            'cf_2639': '' if len(dependent) <= 3 else self.getDocument(dependent[3]['document']['value']),
            'cf_2645': dependent[4]['firstname']['value'] if len(dependent) >= 5 else '',
            'cf_2647': dependent[4]['middlename']['value'] if len(dependent) >= 5 else '',
            'cf_2649': dependent[4]['lastname']['value'] if len(dependent) >= 5 else '',
            'cf_2687': dependent[4]['ssn']['value'] if len(dependent) >= 5 else '',
            'cf_2681': datetime.strptime(dependent[4].dob['value'], '%b %d %Y').strftime('%Y-%m-%d') if len(dependent) >= 5 else '',
            'cf_2679': ('MALE' if dependent[4]['gender']['value'] == 'Male' else 'FEMALE') if len(dependent) >= 5 else '',
            'cf_2719': '' if len(dependent) <= 4 else ('YES' if len(dependent) >= 5 and  dependent[4]['smoke']['value'] == 'Yes' else ('NOT' if len(dependent) >= 5 and  dependent[4]['smoke']['value'] == 'No' else '')),
            'cf_2685': '' if len(dependent) <= 4 else ('YES' if len(dependent) >= 5 and  dependent[4]['pregnant']['value'] == 'Yes' else ('NOT' if len(dependent) >= 5 and  dependent[4]['pregnant']['value'] == 'No' else '')),
            'cf_2699': '' if len(dependent) <= 4 else ('HIJO(A)' if len(dependent) >= 5 and  dependent[4]['relationship']['value'] == 'Son/Daughter' else ('ABUELO(A)' if len(dependent) >= 5 and  dependent[4]['relationship']['value'] == 'Grandparent' else ('PADRE/MADRE' if len(dependent) >= 5 and dependent[4]['document']['value'] == 'Parent' else ('HERMANO(A)' if len(dependent) >= 5 and dependent[4]['document']['value'] == 'Sibling' else ('NIETO(A)' if len(dependent) >= 5 and dependent[4]['document']['value'] == 'Grandchild' else ('SOBRINO(A)' if len(dependent) >= 5 and dependent[4]['document']['value'] == 'Nephew/Niece' else ('TIO(A)' if len(dependent) >= 5 and dependent[4]['document']['value'] == 'Aunt/Uncle' else ('CUÑADO(A)' if len(dependent) >= 5 and dependent[4]['document']['value'] == 'Brother/Sister in-law' else ('YERNO/NUERA' if len(dependent) >= 5 and dependent[4]['document']['value'] == 'Son/Daughter in-law' else ''))))))))),
            'cf_2615': '' if len(dependent) <= 4 else ('OBAMACARE' if len(dependent) >= 5 and dependent[4]['coverage']['label'] == 'Yes' else ('MEDICAID' if len(dependent) >= 5 and dependent[4]['coverage']['label'] == 'Medicaid' else 'NO APLICA')),
            'cf_2683': '' if len(dependent) <= 4 else self.getDocument(dependent[4]['document']['value']),
            'cf_2071': payDict.family['value'],
            'productid': '14x29415',
            'assigned_user_id': '19x113',
            'LineItems':  {
                    'productid': '14x29415',
                    'listprice': '0',
                    'quantity': '1'
            }
        }

    def getPeriod(self, is_renewable: bool, effective_date: str) -> str:
        if not is_renewable:
            date = datetime.strptime(effective_date, '%Y-%m-%d')
            date = date.replace(month=date.month + 1)
            month_translate = {
                'January': 'ENERO',
                'February': 'FEBRERO',
                'March': 'MARZO',
                'April': 'ABRIL',
                'May': 'MAYO',
                'June': 'JUNIO',
                'July': 'JULIO',
                'August': 'AGOSTO',
                'September': 'SEPTIEMBRE',
                'October': 'OCTUBRE',
                'November': 'NOVIEMBRE',
                'December': 'DICIEMBRE'
            }
            return month_translate.get(date.strftime("%B"))

    def getYear(self, effective_date: str) -> str:
        date = datetime.strptime(effective_date, '%m/%d/%Y')
        return str(date.year)

    def getDocument(self, document: str) -> str:
        document_crm = {
            'Citizen': 'CIUDADANO',
            'Resident': 'RESIDENTE',
            'Authorization Work': 'PERMISO DE TRABAJO',
            'Action Notice': 'NOTICIA DE ACCION',
            'Visa': 'VISA',
            'Passport': 'PASAPORTE VIAJERO',
            'Political Asylum': 'ASILO POLITICO'
        }
        return document_crm.get(document, 'OTHER')
