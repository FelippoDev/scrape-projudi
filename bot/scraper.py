from selenium import webdriver
from selenium.webdriver import chrome
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import mysql.connector
import json
import os
from tqdm import tqdm
import base64
from dotenv import load_dotenv
load_dotenv()

def main(token, user, pwd):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(executable_path='bot\chromedriver.exe', chrome_options=chrome_options)


    # LOGIN
    driver.get("https://projudi2.tjpr.jus.br/projudi/usuario/areaAtuacao.do?actionType=selecionar")

    time.sleep(2)
    driver.find_element('id', 'username').send_keys(user)
    driver.find_element('id', "password").send_keys(pwd)
    driver.find_element('xpath', '//*[@id="kc-login"]').click()
    time.sleep(3)
    driver.find_element('id', "totp").send_keys(token)
    driver.find_element('xpath', '//*[@id="kc-login"]').click()
    time.sleep(1)

    driver.get("https://projudi2.tjpr.jus.br/projudi/home.do?r=0.5747265182907446")

    driver.find_element('xpath', '//*[@id="mainPage"]/div[1]/div[2]/div[1]/div[1]/ul/li[1]/span[1]').click()

    time.sleep(1)

    # Path with multiples mandatos
    try:
        theads = driver.find_elements('xpath', '//table[@class="resultTable"]/thead/tr/th[1]')
        # For loop to find in which table we can locate 'central de mandados'
        for i in range(len(theads)):
            if "CENTRAL DE MANDADOS" in theads[i].text:
                break
            
        driver.find_element('xpath', f'//table[@class="resultTable"][{i+1}]/tbody/tr/td/b/a').click()

        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])
        link = driver.find_element('xpath', '//iframe')
        link = link.get_attribute('src')
        driver.get(link)
        driver.find_element('xpath', '//*[@id="tabprefix0"]/table[1]/tbody/tr[4]/td[2]/strong/a').click()
    except:
        print('going to the second path....')

    try:
        # Path with only the central de mandatos
        link = driver.find_element('xpath', '//iframe')
        link = link.get_attribute('src')
        driver.get(link)
        driver.find_element('xpath', '//*[@id="tabprefix0"]/table[1]/tbody/tr[4]/td[2]/strong/a').click()
    except:
        print('going to the third path....')

    # Path selecting oficial de justiça
    try:
        perfis_ativos = driver.find_elements('xpath', '//*[@id="listaPerfilAtivo"]/div/ul/li')
        for perfil in perfis_ativos:
            if 'Oficial de Justiça' in perfil.text:
                perfil.click()
                break
        time.sleep(2)
        link = driver.find_element('xpath', '//iframe')
        link = link.get_attribute('src')
        driver.get(link)
        driver.find_element('xpath', '//*[@id="tabprefix0"]/table[1]/tbody/tr[4]/td[2]/strong/a').click()
    except:
        print('on the third path')

# Fourth path
    try:
        perfis_ativos = driver.find_elements('xpath', '//*[@id="listaPerfilAtivo"]/div/ul/li')
        for perfil in perfis_ativos:
            if 'Oficial de Justiça' in perfil.text:
                perfil.click()
                break
        time.sleep(2)
        driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td[1]/b/a').click()
        driver.switch_to.window(driver.window_handles[-1])
        link = driver.find_element('xpath', '//iframe')
        link = link.get_attribute('src')
        driver.get(link)
        time.sleep(1)
        driver.find_element('xpath', '//*[@id="tabprefix0"]/table[1]/tbody/tr[4]/td[2]/strong/a').click()
    except:
        print('forth path')


    time.sleep(2)

    # Selecting all data in the page
    driver.find_element('xpath', '//*[@id="navigator"]/div[1]/select').click()
    time.sleep(1)
    driver.find_element('xpath', '//*[@id="navigator"]/div[1]/select/option[4]').click()

    driver.execute_script("javascript:document.forms['cumprimentoCartorioMandadoForm']['cumprimentoCartorioMandadoPageSize'].value=document.forms['cumprimentoCartorioMandadoForm']['cumprimentoCartorioMandadoPageSizeOptions'].value;document.forms['cumprimentoCartorioMandadoForm']['cumprimentoCartorioMandadoPageNumber'].value='1';document.forms['cumprimentoCartorioMandadoForm']['cumprimentoCartorioMandadoSortColumn'].value='ccm.prioridade DESC, processoPrioritario.controlePrioridade DESC, recursoPrioritario.controlePrioridade DESC, recursoPrioritario.urgente DESC, ccm.dataOrdenacao ASC';document.forms['cumprimentoCartorioMandadoForm']['cumprimentoCartorioMandadoSortOrder'].value='ASC';document.forms['cumprimentoCartorioMandadoForm'].submit();")
    time.sleep(10)

    # SCRAPPING THE DATA
    all_data = []
    for i in tqdm(range(1, 501)):
        try:
            data = {}

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//table[3]/tbody/tr[{i}]/td[10]'))
            )
            alvo = driver.find_element('xpath', f'//table[3]/tbody/tr[{i}]/td[10]').text
            data_dist = driver.find_element('xpath', f'//table[3]/tbody/tr[{i}]/td[3]').text
            audiencia = driver.find_element('xpath', f'//table[3]/tbody/tr[{i}]/td[7]').text

            lista = []
            start = False
            if audiencia:
                for each in audiencia:
                    if each ==')':
                        break
                    if start:
                        lista.append(each)
                    if each == '(':
                        start = True
                audiencia = ''.join(lista)


                # Indo para a expedicao
            driver.find_element('xpath', f'//table[3]/tbody/tr[{i}]/td[2]/a').click()

                # DADO: Identificador do cumprimento
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[@class='form']/tbody/tr[1]/td[2]"))
            )
            cumprimento_id = driver.find_element('xpath', "//table[@class='form']/tbody/tr[1]/td[2]").text
            n_processo = cumprimento_id.split()[2]
            cumprimento = []
            count = 0
            for c in cumprimento_id:
                cumprimento.append(c)
                if count == 3:
                    break
                count += 1
            cumprimento_id = ''.join(cumprimento)

                # DADO: Natureza de Mandato
            natureza = driver.find_element('xpath', "//table[@class='form']/tbody/tr[6]/td[2]").text

                # DADO: Endereco
            try:
                driver.find_element('xpath', '//table[@class="form"]/tbody/tr[20]')
            except:
                endereco = driver.find_element('xpath', '//table[@class="form"]/tbody/tr[10]/td[2]').text

            else:
                endereco = driver.find_element('xpath', '//table[@class="form"]/tbody/tr[11]/td[2]').text


            try:
                driver.find_element('xpath', '//table[@class="form"]/tbody/tr[20]')
            except:
                # DADO: oficial de justica
                oficial = driver.find_element('xpath', "//table[@class='form']/tbody/tr[18]/td[2]").text
            else:
                    # DADO: oficial de justica
                oficial = driver.find_element('xpath', "//table[@class='form']/tbody/tr[19]/td[2]").text

            #Putting the data in table
            data = {
                'Numero do Processo': n_processo,
                'Alvo': alvo,
                'Natureza': natureza,
                'Oficial de Justiça': oficial,
                'Data Distribuicao': data_dist,
                'Audiencia': audiencia,
                'ID Cumprimento': cumprimento_id,
                'Endereco': endereco,
                }

            all_data.append(data)

            # going back to the table
            driver.execute_script("window.history.go(-1)")
        except:
            break

    print(f'ESTE EH O LENTH DA LISTA ALL DATA {len(all_data)}')
    print(all_data)
    all_data = json.dumps(all_data)
    b64json = all_data.encode("ascii")
    b64json = base64.b64encode(b64json)
    b64json = b64json.decode("ascii")
    db = mysql.connector.connect(
            host='',
            user='',
            password='',
            database='',
            port='',
            auth_plugin='mysql_native_password')

    cursor = db.cursor()
    cursor.execute(f"INSERT INTO scraps (`data`, `username`) VALUES ('"+b64json+"', '"+user+"')")
    db.commit()

