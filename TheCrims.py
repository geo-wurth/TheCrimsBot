import random
import re
import traceback
import _thread as thread
from playsound import playsound
from config import *
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from bs4 import NavigableString
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException

def check_need_login():
    if check_existence(by_id="loginform"):
        return True
    else:
        return False

def login():
    print(get_datetime(), "Trying to login...")
    #Acessa o link principal
    username_field = driver.find_element_by_css_selector('input[placeholder="Username"]')
    password_field = driver.find_element_by_css_selector('input[placeholder="Password"]')

    #username_field.send_keys(Keys.CONTROL + "a")
    #username_field.send_keys(Keys.DELETE)
    username_field.clear()
    username_field.send_keys(USERNAME)

    #password_field.send_keys(Keys.CONTROL + "a")
    #password_field.send_keys(Keys.DELETE)
    password_field.clear()
    password_field.send_keys(PASSWORD)

    button_click(by_css_selector='button[class="btn btn-large btn-inverse"]')

    print(get_datetime(), "The loggin was successfully.\n")

    return

def robbery(need_gang=False):
    #Verifica se está em uma gangue:
    if need_gang:
        print(get_datetime(), "Checking if you'r in a gang...")
        try:
            if check_if_gang_member() == False:
                if enter_virtual_gang_member() == "Error":
                    return
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            return
    
    #Entra no menu de roubo, se for recursivo, pula
    if "#/robberies" not in driver.current_url:
        print(get_datetime(), 'Starting robbery...\n')
        button_click(by_id='menu-robbery')
    else:
        print(get_datetime(), 'Doing robbery loop...')

    button_click(by_id='singlerobbery-select-robbery')
    solo_select = Select(driver.find_element_by_id('singlerobbery-select-robbery'))

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'option[value="1"]')))
    
    try:
        gang_robbery()
        single_robbery()
    except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
        single_robbery()

    return
    
def single_robbery():
    if "#/robberies" not in driver.current_url:
        button_click(by_id='menu-robbery')
        
    #Tenta acessar o menu de seleção de roubo solo
    solo_select = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'singlerobbery-select-robbery')))
    button_click(by_element=solo_select)
    solo_select = Select(solo_select)

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('option[value="' + str(PREFERED_SOLO_ROBBERY) + '"]'))))
    #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'option[value="43"]')))
    
    #Pega os dados dos roubos
    robbery_src = driver.page_source
    robbery_soup = BeautifulSoup(robbery_src, 'lxml')
    robbery_soup = robbery_soup.find_all("select")
    #robbery_soup[0] - Entrega a lista do single_robbery
    #robbery_soup[1] - Entrega a lista do gang_robbery
    
    #Encontra o melhor roubo single
    single_robbery_soup = robbery_soup[0].find_all("option")
    single_robbery_types = []
    for single_robbery_select in single_robbery_soup:
        if single_robbery_select == single_robbery_soup[0]:
            continue
        single_robbery_options = []
        single_robbery_info = str(single_robbery_select.text)
        single_robbery_value = int(single_robbery_select.attrs['value'])
        single_robbery_info = single_robbery_info.strip()
        single_robbery_info = single_robbery_info.split("-")
        single_robbery_sub_info = single_robbery_info[len(single_robbery_info)-1].split()
        single_robbery_stamina = single_robbery_sub_info[0]
        single_robbery_stamina = single_robbery_stamina.strip().replace("%", "")
        single_robbery_stamina = int(single_robbery_stamina)
        single_robbery_sp = single_robbery_sub_info[-1]
        single_robbery_sp = single_robbery_sp.strip().replace("%", "")
        single_robbery_sp = int(single_robbery_sp)
        single_robbery_options.append(single_robbery_info[0].strip())
        single_robbery_options.append(single_robbery_value)
        single_robbery_options.append(single_robbery_stamina)
        single_robbery_options.append(single_robbery_sp)
        single_robbery_types.append(single_robbery_options)
    single_robbery_types.sort(key=lambda  x: (x[3],x[1]), reverse=True)

    #Seleciona a opção de roubo solo
    #elem.select_by_value(str(single_robbery_types[0][1])) #Pela listagem
    solo_select.select_by_value(PREFERED_SOLO_ROBBERY) #Pelo arquivo config.py

    #Verifica Stamina e Addiction
    print(get_datetime(), "Checking Stamina and Addiction...")
    sleep(2)
    #stamina_needed = single_robbery_types[0][2] #Ordenado pela listagem

    try: #Ordenado pelo arquivo config.py
        for each_option in single_robbery_types:
            if each_option[1] == int(PREFERED_SOLO_ROBBERY):
                stamina_needed = each_option[2]
                break
    except (ValueError, TypeError) as e:
        print(get_datetime(), "Error - Wrong configuration!")
        quit_program()
    
    if check_stamina_low(stamina_needed) == False:
        if check_addiction_high() == True:
            hospital()
            return
    else:
        night_life()
        return
    
    button_click(by_id='singlerobbery-rob')
    print(get_datetime(), "The solo robbery was successfully!\n")

    return

def gang_robbery():
    elements_to_wait = [["Select", "gangrobbery-select-robbery", "by_id"],["Accept", "gangrobbery-accept", "by_id"],["Exectue", "gangrobbery-execute", "by_id"],["Abort", "gangrobbery-abort", "by_id"]]
    gang_elements = wait_for_one_of_several(5, elements_to_wait)
    if gang_elements == None:
        global virtual_gang
        virtual_gang = True
        return
    
    #Tenta fazer um plano de roubo
    if USE_VIRTUAL_GANG == False:
        try:
            print(get_datetime(),"Checking if it is possibly to plan a gang robbery...")
            #Tenta acessar o menu de seleção de roubo de gangue
            if driver.find_element_by_id('gangrobbery-select-robbery') != None:
                button_click(by_id='gangrobbery-select-robbery')
            gangue_select = Select(driver.find_element_by_id('gangrobbery-select-robbery'))

            #Pega os dados dos roubos
            gang_robbery_src = driver.page_source
            gang_robbery_soup = BeautifulSoup(gang_robbery_src, 'lxml')
            gang_robbery_soup_select = gang_robbery_soup.find_all("select")
            #robbery_soup[0] - Entrega a lista do single_robbery
            #robbery_soup[1] - Entrega a lista do gang_robbery

            #Encontra o melhor roubo de gangue
            if len(gang_robbery_soup_select) == 2:
                gang_robbery_soup_option = gang_robbery_soup_select[1].find_all("option")
                gang_robbery_types = []
                for gang_robbery_select in gang_robbery_soup_option:
                    if gang_robbery_select == gang_robbery_soup_option[0]:
                        continue
                    gang_robbery_options = []
                    gang_robbery_info = str(gang_robbery_select.text)
                    gang_robbery_value = int(gang_robbery_select.attrs['value'])
                    gang_robbery_name = gang_robbery_info.strip()
                    gang_robbery_options.append(gang_robbery_name)
                    gang_robbery_options.append(gang_robbery_value)
                    gang_robbery_types.append(gang_robbery_options)
                gang_robbery_types.sort(key=lambda  x: (x[1]), reverse=True)

            gangue_select.select_by_value(PREFERED_GANG_ROBERRY)
            sleep(2)

        except (ValueError, TypeError, NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            pass
        
    try:
        driver.find_element_by_css_selector('table[class="table table-condensed"]')
    except (NoSuchElementException, StaleElementReferenceException) as e:
        button_click(by_css_selector="h3")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="table table-condensed"]')))

    ##Verifica Stamina e Addiction
    print(get_datetime(), "Checking Stamina and Addiction...")
    gang_robbery_src = driver.page_source
    gang_robbery_soup = BeautifulSoup(gang_robbery_src, 'lxml')
    stamina_needed_tr = gang_robbery_soup.find('table', class_="table table-condensed")
    stamina_needed_tr = stamina_needed_tr.find_all('tr')
    for each_tr in stamina_needed_tr:
        each_tr_info = str(each_tr)
        if "Stamina required:" in each_tr_info:
            stamina_needed = each_tr_info.strip().replace("<tr><td>Stamina required:</td> <td>", "")
            stamina_needed = stamina_needed.strip().replace("%</td></tr>", "")
            stamina_needed = int(stamina_needed)
            break

    if check_stamina_low(stamina_needed) == False:
        if check_addiction_high() == True:
            hospital()
            return
    else:
        night_life()
        return

    try:
        #Aguarda carregar a função da página
        button_click(by_id='gangrobbery-plan')
        print(get_datetime(),"Gang robbery plan was sucessfully!\n")
    except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
        pass

    #Tenta aceitar e/ou executar um plano roubo de gangue
    #Tenta aceitar um plano
    #print(get_datetime(),"Nope... we can't do a robbery plan...")
    #print(get_datetime(),"Trying to accept a gang robbery plan...")

    elements_to_wait = [["Accept", "gangrobbery-accept", "by_id"],["Exectue", "gangrobbery-execute", "by_id"],["Abort", "gangrobbery-abort", "by_id"]]
    wait_for_one_of_several(5, elements_to_wait)
        
    accept_button = driver.find_element_by_id('gangrobbery-accept')
    if "display: none" not in str(accept_button.get_attribute('outerHTML')):
        button_click(by_element=accept_button)
        print(get_datetime(),"Gang robbery plan was accepted successfully!\n")
        sleep(3)
    #else:
        #print(get_datetime(),"Nahhh, we've failed to accept a gang robbery plan...")

    #Tenta executtar um plano
    #print(get_datetime(),"Trying to execute a gang robbery plan...")
    execute_button = driver.find_element_by_id('gangrobbery-execute')
    if "display: none" not in str(execute_button.get_attribute('outerHTML')):
        button_click(by_element=execute_button)
        print(get_datetime(),"Gang robbery plan was executed successfully!\n")
    #else:
        #print(get_datetime(),"Sry, the gang robbery has failed...")
        #print(get_datetime(), "Let's try some solo robbery!\n")

def night_life():
    global drugs_ok
    drugs_ok = False
    while drugs_ok == False:
        try:
            #Acessa a vida noturna
            print(get_datetime(), "Accessing Nightlife...")
            button_click(by_id='menu-nightlife')

            #Verifica se tem tickets para acessar a casa de show
            print(get_datetime(), "Checking Tickets...")
            if check_tickets_low():
                night_life_count_down()
                return
            else:
                print("")
            
            print(get_datetime(), "Acessing night club...")

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class="btn btn-inverse btn-small pull-right"]')))
            sleep(1) #Aguarda o restante dos botões carregar

            #Entra na sala
            enter = driver.find_elements_by_css_selector('button[class="btn btn-inverse btn-small pull-right"]')
            for each_enter in enter:
                try:
                    button_click(by_element=each_enter)
                except ElementNotVisibleException as e:
                    #Verifica se o botão existe
                    pass
                except StaleElementReferenceException as e:
                    #Verifica se já entrou na sala
                    break
                sleep(1)

            night_club()
        except:
            raise NoSuchElementException
    return

def night_club():
    print(get_datetime(), "Night club successfully accessed!")
    thread.start_new_thread(nightclub_people, ()) #New thread for escape before killed

    #Aguarda a página carregar
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="table table-condensed table-top-spacing"]')))
    sleep(1) #Aguarda o restante dos botões carregar
    
    #Code for Beautiful Soup - Escolher a drogra
    night_life_src = driver.page_source
    night_life_soup = BeautifulSoup(night_life_src, 'lxml')
    night_life_drugs = night_life_soup.find("table", class_='table table-condensed table-top-spacing')
    night_life_drugs = night_life_drugs.find("tbody")
    room_drugs = []
    for night_life_drugs_tr in night_life_drugs.find_all('tr'):
        drugs_data = []
        for night_life_drugs_td in night_life_drugs_tr.find_all('td'):

            try:
                drug_info = str(night_life_drugs_td.text)
            except (TypeError, NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
                continue
            
            if "%" in drug_info:
                stamina_drug = drug_info
                stamina_drug = stamina_drug.strip().replace("%", "")
                stamina_drug = float(stamina_drug)
                drugs_data.append(stamina_drug)
            elif "$" in drug_info:
                drug_value = drug_info
                drug_value = drug_value.strip().replace("$", "")
                drug_value = int(drug_value)
                drugs_data.append(drug_value)
            elif "Buy" not in drug_info:
                drug_name = drug_info
                drugs_data.append(drug_name)
        drugs_data.append(drug_value/stamina_drug)
        drugs_data.insert(0,len(room_drugs))
        room_drugs.append(drugs_data)
    room_drugs.sort(key=lambda  x: (x[4]))

    #Code for Selenium - Escolher a droga
    night_life_drugs_selenium = driver.find_element_by_css_selector('table[class="table table-condensed table-top-spacing"]')
    night_life_drugs_selenium = night_life_drugs_selenium.find_element_by_tag_name('tbody')
    drug_element = night_life_drugs_selenium.find_elements_by_tag_name('tr')
    drug_qtt_to_buy = round((100 - get_stamina())/room_drugs[0][2]) + 1
    print(get_datetime(), "Drug to buy:", room_drugs[0][1])
    print(get_datetime(), "Qtt of drugs to buy:", drug_qtt_to_buy)    

    #Verifica cash e compra a droga:
    cash_needed = drug_qtt_to_buy * room_drugs[0][2]
    cash = get_cash()
    if cash < cash_needed:
        button_click(by_css_selector='button[class="btn btn-inverse btn-large pull-right"]')
        bank(True, cash_needed - cash)
        print("Let's try again to go to nightlife...\n")
        night_life()
        return

    #Compra a droga
    drug_qtt_field = drug_element[room_drugs[0][0]].find_element_by_name('quantity')
    qtt_drug_bought = 0
        
    while qtt_drug_bought < drug_qtt_to_buy:
        if check_stamina_low(100):
            if (drug_qtt_to_buy - qtt_drug_bought) > 99:
                drugs_new_qtt_to_buy = 99
            else:
                drugs_new_qtt_to_buy = drug_qtt_to_buy - qtt_drug_bought

            #drug_qtt_field.clear()
            drug_qtt_field.send_keys(Keys.CONTROL + "a")
            drug_qtt_field.send_keys(Keys.DELETE)
            drug_qtt_field.send_keys(drugs_new_qtt_to_buy)
            buy_button = drug_element[room_drugs[0][0]].find_element_by_css_selector('button[class="btn btn-inverse btn-small"]')
            button_click(by_element=buy_button)
            qtt_drug_bought += drugs_new_qtt_to_buy
            sleep(2)
        else:
            break

    if check_stamina_low(100) == True:
        night_club()

    exit_buttons = driver.find_elements_by_css_selector('button[class="btn btn-inverse btn-large pull-right"]')
    for each_exit_button in exit_buttons:
        if 'Exit' in each_exit_button.text:
            button_click(by_element=each_exit_button)
    
    print(get_datetime(), "The drug was bought successfully!\n")
    global drugs_ok
    drugs_ok = True
    bank()
    return

def nightclub_people():
    #timer = 30
    global drugs_ok
    #while (timer >= 0) or (drugs_ok == False):
    while drugs_ok == False:
        if "#/nightlife/nightclub" not in driver.current_url:
            return
        
        try:
            driver.find_element_by_id('nightclub-singleassault-attack')
            if PEOPLE_ON_NIGHTCLUB == 0: #Run away
                #Click on Exit Button
                exit_buttons = driver.find_elements_by_css_selector('button[class="btn btn-inverse btn-large pull-right"]')
                for each_exit_button in exit_buttons:
                    if 'Exit' in each_exit_button.text:
                        button_click(by_element=each_exit_button)
                print(get_datetime(), "You have just escaped from another person in night club!")
                warning_sound('escaped')
                return
                    
            elif PEOPLE_ON_NIGHTCLUB == 1: #Attack everyone
                #Get first enemy username
                enemy_name = driver.find_element_by_css_selector('img[width="32"][height="40"][border="0"]')
                enemy_name = enemy_name.get_attribute('data-username')

                #Select the enemy in the dropdown list
                enemy_select = driver.find_element_by_id('nightclub-singleassault-select-victim')
                enemy_select = enemy_selectfind_element_by_css_selector('button[data-toggle="dropdown"][class="btn btn-inverse dropdown-toggle"]')
                button_click(by_element=enemy_select)
                #enemy_select = Select(enemy_select)
                #enemy_selectselect_by_visible_text(enemy_name)
                enemy_select.send_keys(enemy_name)

                #Attack the selected enemy
                enemy_attack = driver.find_element_by_id('nightclub-singleassault-attack')
                if 'Attack' in enemy_attack.text:
                    button_click(by_element=enemy_attack)

                print(get_datetime(), "You have just attacked", enemy_name)
                
            elif PEOPLE_ON_NIGHTCLUB == 2: #Attac only lower respect
                #Get enemy respect
                enemy_respect = driver.find_element_by_css_selector('div[class="user_list_respect"]')
                enemy_respect = enemy_respect.text
                enemy_respect = enemy_respect.split()
                enemy_respect = int(enemy_respect[-1])
                print(get_datetime(), "This function is not implemented yet!\n")
                
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            pass
        #timer -= 1
        sleep(0.5)
    
def hospital():
    #Acessa o hospital
    print(get_datetime(), "Accessing Hospital...")
    button_click(by_id='menu-hospital')

    #Localiza o valor para desintoxicar
    sleep(4)
    detox_value = driver.find_element_by_css_selector('button[class="btn btn-small btn-inverse pull-left"]')
    detox_value = str(detox_value.text)
    if "Price:" in detox_value:
        detox_value = detox_value.strip().replace("Price: $", "")
        detox_value = int(detox_value.strip().replace(",", ""))
    else:
        detox_value_p_tag = driver.find_elements_by_css_selector('p')
        for each_p_tag in detox_value_p_tag:
            detox_value = str(each_p_tag.text)
            if "Price:" in detox_value:
                detox_value = detox_value.strip().replace("Price: $", "")
                detox_value = int(detox_value.strip().replace(",", ""))
                break

    #Se tiver dinheiro se desintoxica
    print(get_datetime(), "Detox value:", detox_value)
    cash = int(get_cash())
    if detox_value <= cash:
        button_click(by_css_selector='button.btn.btn-small.btn-inverse.pull-left')
        print(get_datetime(), "Detox was made successfully!\n")
        if get_cash() > 0:
            sleep(2)
            bank()
            return
        else:
            return
    else:
        print(get_datetime(), "No money in hand, lets withdrawn some for a detox!\n")
        sleep(2)
        bank(True, detox_value - cash)
        print(get_datetime(), "Let's try to be detoxicated again!\n")
        sleep(2)
        hospital()
    sleep(2)
    bank()
    return

def bank(withdraw=False, cash_needed=0):
    #Acessa o banco
    print(get_datetime(), "Accessing Bank...")
    
    button_click(by_id='menu-bank')
    sleep(4)

    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'button.btn.btn-inverse')))

    #Define o valor a ser movimentado
    cash = get_cash()
    money_bank = get_money_bank()
    minimum_cash = int((cash + money_bank) * ((PERCENT_OF_ALL_CASH_TO_HAND) / 100))
    
    if withdraw:
        if cash_needed < minimum_cash:
            move_money = cash_needed
        else:
            move_money = minimum_cash
    else:
        if cash > minimum_cash:
            move_money = cash - minimum_cash
        else:
            withdraw = True
            move_money = minimum_cash - cash
            if move_money == 0:
                return
            
    #Acessa o input field para movimentar o dinheiro
    input_field_bank = driver.find_element_by_css_selector('input[type="text"][maxlength="20"][style="width: 100px;"]')
    input_field_bank.send_keys(Keys.BACKSPACE)
    input_field_bank.send_keys(move_money)

    #Escolhe a opção de withdraw ou deposit
    bank_option = driver.find_element_by_tag_name('select')
    for each_option in bank_option.find_elements_by_css_selector('option'):
        option_text = str(each_option.text)
        if ('Withdraw' in option_text) and withdraw:
            option_select = Select(bank_option)

            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'option[value="withdraw"]')))
            except TimeoutException as e:
                pass
            
            if withdraw:
                option_select.select_by_value("withdraw")
            else:
                option_select.select_by_value("deposit")
    
    #Aperta o botão de Transferir Fundos
    buttons_bank = driver.find_elements_by_css_selector('button.btn.btn-inverse')
    for each_button in buttons_bank:
        button_text = each_button.text
        button_text = button_text.strip()
        if button_text == "Transfer money":
            button_click(by_element=each_button)
            break

    #Imprimi a msg de sucesso
    sleep(2)
    if withdraw:
        print(get_datetime(), "Withdraw was successfully!")
        print(get_datetime(), "New cash in hand is:", get_cash(), "\n")
    else:
        print(get_datetime(), "Deposit was successfully!")
        print(get_datetime(), "New cash in bank is:", cash + money_bank, "\n")

    sleep(1)
    return

def casino():
    #Inicia o casino
    print(get_datetime(), "Accessing Casino...")
    button_click(by_id='menu-casino')

    #Acessa o jogo de dado
    print(get_datetime(), "Acessing Dice Game...")
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#/casino/dicegame"]')))
    button_click(by_css_selector='a[href="#/casino/dicegame"]')

    #Procura e compra o jogo gratuito
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="well well-small"]')))
    dice_games = driver.find_elements_by_css_selector('div[class="well well-small"]')
    for each_dice_game in dice_games:
        dice_game_info = str(each_dice_game.find_element_by_tag_name('h4').text)
        if "Free!" in dice_game_info:
            buy_button = each_dice_game.find_element_by_css_selector('button[class="btn btn-inverse"]')
            button_click(by_element=buy_button)
            print(get_datetime(), "The new day free dice was bought!\n")
            sleep(2)
    return    

def get_money_bank():
    #Pega o total de grana no banco
    money = str(driver.find_element_by_tag_name('h4').text)
    money = money.strip().replace("Money in bank: $", "")
    money = money.strip().replace(",", "")
    money = int(money)
    print(get_datetime(), "Cash in bank:", money)
    return money
        
def get_cash():
    #Pega a grana na mão
    cash_find = driver.find_elements_by_css_selector('div.text-center')
    cash_value = None
    for each_div in cash_find:
        if cash_value != None:
            break
        inner_HTML_cash_div = str(each_div.get_attribute('innerHTML'))
        if "Cash" in inner_HTML_cash_div:
            for each_new_div in each_div.find_elements_by_css_selector('div'):
                if cash_value != None:
                    break
                inner_HTML_cash_new_div = str(each_new_div.get_attribute('innerHTML'))
                if "Cash" in inner_HTML_cash_new_div:
                    for each_span in each_new_div.find_elements_by_css_selector('span'):
                        if cash_value != None:
                            break
                        if str(each_span.text) != "":
                            cash_value = each_span.text

    cash_value = cash_value.strip().replace("$", "")
    cash_value = cash_value.strip().replace(",", "")
    cash_value = int(cash_value)
    print(get_datetime(), "Cash in hand:", cash_value)
    return cash_value

def get_single_robbery_power():
    #Pega o poder de roubo
    power_robber = driver.find_element_by_xpath('//*[@id="content_right"]/div/div[8]/div[1]/a')
    for span_tag in power_robbery.attrs['span']:
        robbery_power = long(span_tag.text)
        if robbery_power > 2:
            print(get_datetime(), "Robbery Power:", robbery_power)
            return span_tag.text

def get_respect():
    #Pega o respeito
    user_info = driver.find_element_by_id('user-profile-info')
    for div_tag in user_info.attr['div']:
        if div_tag.text == "Respeito":
            respect = div_tag.attrs['span'].text
            print(get_datetime(), "Respect:", respect)
            return respect

def check_if_gang_member():
    if "gang#/" not in driver.current_url:
        driver.get("https://www.thecrims.com/gang#/")

    gang_text = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')))

    if "Gang center" in str(gang_text.text):
        return False
    else:
        return True

def enter_virtual_gang_member():
    if "gang#/" not in driver.current_url:
        driver.get("https://www.thecrims.com/gang#/")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="table table-condensed"]')))

    gang_available = []

    gang_table = driver.find_element_by_css_selector('table[class="table table-condensed"]')
    gang_table = gang_table.find_element_by_css_selector('tbody')
    gang_table = gang_table.find_elements_by_css_selector('tr')
    for each_gang in gang_table:
        gang_available_info = []
        gang_info = each_gang.find_elements_by_css_selector('td')
        for each_info in gang_info:
            gang_available_info.append(str(each_info.text))
        gang_available_info[2] = int(gang_available_info[2])
        gang_available_info[3] = int(gang_available_info[3])
        gang_available_info[4] = int(gang_available_info[4])
        gang_available_info.insert(0,len(gang_available))
        gang_available.append(gang_available_info)

    gang_available.sort(key=lambda  x: (x[3]), reverse=True)

    join = driver.find_elements_by_css_selector('input[value="Join"][class="btn btn-inverse btn-mini"]')
    for i in range(len(gang_available)):
        try:
            button_click(by_element=join[gang_available[i][0]])
        except ElementNotVisibleException as e:
            #Verifica se o botão existe
            pass
        except StaleElementReferenceException as e:
            #Verifica se já entrou na sala
            break
        sleep(1)
    try:
        alert_message = driver.find_element_by_css_selector('div[class="alert alert-danger"]')
        if alert_message.text != None:
            print(get_datetime(), "We can't join in a gang right now!\n")
        return
    except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
        print(get_datetime(), "Entered in a new virtual gang!\n")
        return "Error"

def get_stamina():
    #Pega o valor da stamina
    stamina = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'stamina-progressbar')))
    #stamina = driver.find_element_by_id('stamina-progressbar')
    stamina = stamina.get_attribute("style")
    stamina = stamina.strip().replace("width: ", "")
    stamina = stamina.strip().replace("%;", "")
    stamina = int(stamina)
    return stamina

def check_tickets_low():
    #Verifica se os tickets estão baixos
    tickets_src = driver.page_source
    tickets_soup = BeautifulSoup(tickets_src, 'lxml')
    tickets_div = tickets_soup.find("div", id="user-profile-info")

    for div_tag in tickets_div.find_all("div"):
        if "Tickets: " in div_tag.text:
            tickets = div_tag.text
            tickets = tickets.strip().replace("Tickets: ", "")
            break
            
    print(get_datetime(), "Tickets:", tickets)
    if int(tickets) < TICKETS_STOP:
        print(get_datetime(), "Tickets lower than " + str(TICKETS_STOP) + ", waiting for " + str(TICKETS_TO_RECOVER) + " tickets to recover...\n")
        return True
    else:
        return False

def check_stamina_low(stamina_needed):
    #Verifica se a stamina está baixa
    stamina = get_stamina()
    print(get_datetime(), "Stamina:",stamina)
    if int(stamina) < stamina_needed:
        print(get_datetime(), "Your stamina is very low, you need to recover it!\n")
        return True
    else:
        return False

def check_addiction_high():
    #Verifica se o addiction está alto
    addiction = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'addiction-progressbar')))
    #addiction = driver.find_element_by_id('addiction-progressbar')
    addiction = addiction.get_attribute("style")
    addiction = addiction.strip().replace("width: ", "")
    addiction = addiction.strip().replace("%;", "")
    print(get_datetime(), "Addiction:", addiction)
    if int(addiction) >= MAX_ADDICTION:
        print(get_datetime(), "Your addiction is too high, go to the hospital for a detox!\n")
        return True
    else:
        return False
     
def check_existence(by_xpath=None, by_id=None, by_css_selector=None):
    #Verifica se o XPath existe
    if by_xpath != None:
        try:
            driver.find_element_by_xpath(by_xpath)
            return True
        except NoSuchElementException as e:
            return False

    #Verifica se o ID existe
    elif by_id != None:
        try:
            driver.find_element_by_id(by_id)
            return True
        except NoSuchElementException as e:
            return False    

    #Verifica se o css selector existe
    elif by_css_selector != None:
        try:
            driver.find_elements_by_css_selector(by_css_selector)
            return True
        except NoSuchElementException as e:
            return False

def button_click(by_id=None, by_css_selector=None, by_xpath=None, by_element=None):
    if by_id != None:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, by_id)))
        button = driver.find_element_by_id(by_id)
        try:
            button.click()
        except ElementClickInterceptedException as e:
            driver.execute_script("arguments[0].click();", button)
        
    elif by_css_selector != None:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, by_css_selector)))
        button = driver.find_element_by_css_selector(by_css_selector)
        try:
            button.click()
        except ElementClickInterceptedException as e:
            driver.execute_script("arguments[0].click();", button)
        
    elif by_xpath != None:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, by_xpath)))
        button = driver.find_element_by_xpath(by_xpath)
        try:
            button.click()
        except ElementClickInterceptedException as e:
            driver.execute_script("arguments[0].click();", button)

    elif by_element != None:
        try:
            by_element.click()
        except ElementClickInterceptedException as e:
            driver.execute_script("arguments[0].click();", by_element)

def check_update_count_down():
    update_screen = driver.find_element_by_tag_name('h1')
    if update_screen.text == 'Daily updates in process':
        return True
    else:
        return False

def get_update_count_down():
    update_screen = driver.find_element_by_tag_name('h1')
    if update_screen.text == 'Daily updates in process':
        get_time = driver.find_elements_by_tag_name('p')
        days = 0
        hours = 0
        minutes = 0
        seconds = 0
        for each_get_time in get_time:
            time_description = str(each_get_time.text)
            if "day(s)" in time_description:
                days = time_description
                days = days.strip().replace("day(s)", "")
                days = int(days)
            elif "hour(s)" in time_description:
                hours = time_description
                hours = hours.strip().replace("hour(s)", "")
                hours = int(hours)
            elif "minute(s)" in time_description:
                minutes = time_description
                minutes = minutes.strip().replace("minute(s)", "")
                minutes = int(minutes)
            elif "second(s)" in time_description:
                seconds = time_description
                seconds = seconds.strip().replace("second(s)", "")
                seconds = int(seconds)
    total_time = (days*24*60*60) + (hours*60*60) + (minutes*60) + (seconds)
    print(get_datetime(), "Update in process...")
    return total_time

def check_emergency():
    if "#/hospital" not in driver.current_url:
        button_click(by_id='menu-hospital')

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p')))
    emergency = driver.find_element_by_tag_name('H1')
    emergency = str(emergency.text)
    if 'Emergency' in emergency:
        print(get_datetime(), "You're dead! =[")
        return True
    else:
        print(get_datetime(), "You're not dead! =]")
        return False

def get_emergency_count_down():
    if "#/hospital" not in driver.current_url:
        button_click(by_id='menu-hospital')

    emergency = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p')))
    #emergency = driver.find_element_by_tag_name('p')
    emergency_count_down = str(emergency.text)
    emergency_time_index_beg = emergency_count_down.index("Day ") + 4
    emergency_time_index_end = emergency_count_down.index("You are a mess") - 2
    emergency_count_down = emergency_count_down[emergency_time_index_beg:emergency_time_index_end]
    emergency_count_down = re.split('\s|:', emergency_count_down)
    for each_time in range(len(emergency_count_down)):
        emergency_count_down[each_time] = int(emergency_count_down[each_time])
    return emergency_count_down

def check_arrested():
    if "#/prison" not in driver.current_url:
        button_click(by_id='menu-prison')
    prison = driver.find_element_by_tag_name('h1')
    prison = str(prison.text)
    if "prison" in prison.lower():
        print(get_datetime(), "You got arrested! =[")
        return True
    else:
        print(get_datetime(), "You're not arrested! =]")
        return False

def get_arrest_count_down():
    if "#/prison" not in driver.current_url:
        button_click(by_id='menu-prison')

    prison = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'statusbox')))
    #prison = driver.find_element_by_id('statusbox')
    prison = prison.find_element_by_css_selector('span')
    arrest_count_down = str(prison.text)
    arrest_count_down = arrest_count_down.strip().replace("You will be released day ", "")
    arrest_count_down = arrest_count_down.strip().replace(".", "")
    arrest_count_down = re.split('\s|:', arrest_count_down)
    for each_time in range(len(arrest_count_down)):
        arrest_count_down[each_time] = int(arrest_count_down[each_time])

    return arrest_count_down

def get_game_datetime():
    game_datetime = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'game-time')))
    #game_datetime = driver.find_element_by_id('game-time')
    game_datetime = str(game_datetime.get_attribute('innerHTML'))
    game_datetime = game_datetime.strip().replace("Day", "")
    game_datetime = game_datetime.lstrip()
    game_datetime = re.split('\s|:', game_datetime)

    for each_time in range(len(game_datetime)):
        game_datetime[each_time] = int(game_datetime[each_time])
    #print("Game Date & Time:", game_datetime)
    return game_datetime

def calculate_dif_game_dt(future_game_dt):
    days = 0
    hours = 0
    minutes = 0
    actual_game_dt = get_game_datetime()
    if future_game_dt[0] > actual_game_dt[0]:
        days = future_game_dt[0] - actual_game_dt[0]
    if future_game_dt[1] > actual_game_dt[1]:
        hours = future_game_dt[1] - actual_game_dt[1]
    elif (future_game_dt[1] < actual_game_dt[1]) and (days > 0):
        hours = ((future_game_dt[1] + 24) - actual_game_dt[1])
        days -= 1
    if future_game_dt[2] > actual_game_dt[2]:
        minutes = future_game_dt[2] - actual_game_dt[2]
    elif (future_game_dt[2] < actual_game_dt[2]) and ((hours > 0) or (days > 0)):
        minutes = (future_game_dt[2] + 60) - actual_game_dt[2]
        hours -= 1
        if (hours < 0) and (days > 0):
            days -= 1
            hours = 24 + hours
    days = days * 24 * 60 * 60
    hours = hours * 60 * 60
    minutes = minutes * 60
    dif_game_time = days + hours + minutes
    return dif_game_time

def convert_game_dt_rl_dt(game_datetime):
    rl_dt = int(calculate_dif_game_dt(game_datetime) / 4)
    return rl_dt

def get_datetime():
    date_time = datetime.now().strftime('<%d-%m-%Y %H:%M:%S>')
    return date_time

def countdown_timer(t):
    warning_sound('timer_start')
    while t:
        mins, secs = divmod(t, 60)
        hrs, mins = divmod(mins, 60)
        timeformat = 'Countdown timer to restart: {:02d}:{:02d}:{:02d}'.format(hrs, mins, secs)
        print(get_datetime(), timeformat, end='\r')
        sleep(1)
        t -= 1
    warning_sound('timer_finish')

def night_life_count_down():
    print(get_datetime(),"We've to wait to continue...")
    waiting_time = TICKETS_TO_RECOVER * 300
    waiting_time = random.randint(waiting_time, waiting_time * int((PERCENTAGE_OF_ADICIONAL_WAITING + 100) / 100))
    countdown_timer(waiting_time)
    driver.refresh()
    if check_need_login():
        casino()
    return

def quit_program():
    #Finaliza o bot
    def quit_program_recursively():
        try:
            exit_answer = input(str(get_datetime()) + " Do you want to exit?? (Y/N): ")
            if exit_answer.lower() == 'n':
                print("")
                return
            elif exit_answer.lower() == 'y':        
                print(get_datetime(), "Exiting the program...")
                driver.quit()
                raise SystemExit
                exit
            else:
                print(get_datetime(), "Invalid option, try again!")
                quit_program_recursively()
        except (KeyboardInterrupt, TypeError, ValueError) as e:
            quit_program_recursively()

    print("\n" + str(get_datetime()), "The bot was stopped by user...")
    quit_program_recursively()

def warning_sound(file=None):
    if PLAY_SONGS:
        if file == "timer_start":
            playsound('songs\\timer_started.mp3')
        elif file == "timer_finish":
            playsound('songs\\timer_finished.mp3')
        elif file == "dead":
            playsound('songs\\dead.mp3')
        elif file == "arrested":
            playsound('songs\\arrested.mp3')
        elif file == "update":
            playsound('songs\\update.mp3')
        elif file == "escaped":
            playsound('songs\\escape.mp3')
    else:
        return

def wait_for_one_of_several(time, elements):
    for i in range(time):
        for each_element in elements:
            if each_element[2] == 'by_id':
                try:
                    driver.find_element_by_id(each_element[1])
                    return each_element[0]
                except NoSuchElementException as e:
                    pass
            elif each_element[2] == 'by_css_selector':
                try:
                    driver.find_element_by_css_selector(each_element[1])
                    return each_element[0]
                except NoSuchElementException as e:
                    pass
            elif each_element[2] == 'by_xpath':
                try:
                    driver.find_element_by_xpath(each_element[1])
                    return each_element[0]
                except NoSuchElementException as e:
                    pass
        sleep(1)

options = Options()
#options.add_argument('--headless') #Janela do Chrome modo hidden
options.add_argument('--log-level=3') #Impede a criação do arquivo debug.log
options.add_argument("--incognito") #Modo incógnito do chrome
options.add_argument("--start-maximized") #Inicia em modo maximizado
#options.add_argument('--disable-logging')
#options.add_argument("--no-sandbox")
#options.add_argument("--disable-setuid-sandbox")
#options.add_argument("--disable-notifications")
#options.add_argument("--disable-gpu")
#options.add_argument('disable-infobars')
#options.add_experimental_option('excludeSwitches', ['enable-logging'])
#options.add_argument("--disable-infobars")
#options.add_experimental_option("prefs", { \
#    "profile.default_content_setting_values.notifications": 2 # 1:allow, 2:block 
#})

driver = webdriver.Chrome(options=options)
driver.get('https://www.thecrims.com/')

#Faz o login no site e inicializa o bot
print(get_datetime(), "The Crims BOT - http://www.thecrims.com")
print(get_datetime(), "Developed by @geo-wurth (github)")
print(get_datetime(), "Version 1.0\n")
        
print(get_datetime(), "After it starts, press Ctrl+C to stop it\n")

global virtual_gang

while True:
    try:
        if check_need_login():
            login()
            if USE_VIRTUAL_GANG:
                virtual_gang = True
            else:
                virtual_gang = False
            new_day = False
        try:
            try:
                if virtual_gang:
                    robbery(virtual_gang)
                    virtual_gang = False
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                pass
            if new_day:
                new_day = False
                casino()
                robbery()
            else:
                robbery()
                pass
        except KeyboardInterrupt:
            quit_program()
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            print(get_datetime(),"Oh, no! Some error has occurred, let's try to identify it...")
            waiting_time = 0
            try:
                print(get_datetime(),"Verifying if its a update...")
                if check_update_count_down():
                    warning_sound('update')
                    new_day = True
                    waiting_time = get_update_count_down()
                else:
                    raise NoSuchElementException
            except KeyboardInterrupt:
                quit_program()
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                try:
                    print(get_datetime(),"Verifying if you got killed...")
                    if check_emergency():
                        warning_sound('dead')
                        waiting_time = convert_game_dt_rl_dt(get_emergency_count_down())
                    else:
                        raise NoSuchElementException
                except KeyboardInterrupt:
                    quit_program()
                except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                    try:
                        print(get_datetime(),"Verifying if you got arrested...")
                        if check_arrested():
                            warning_sound('arrested')
                            waiting_time = convert_game_dt_rl_dt(get_arrest_count_down())
                            print("Waiting time:", waiting_time)
                        else:
                            raise NoSuchElementException
                    except KeyboardInterrupt:
                        quit_program()
                    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                        pass

            if waiting_time != 0:
                print(get_datetime(),"We've to wait to continue...")
                waiting_time = random.randint(waiting_time, (waiting_time * int((PERCENTAGE_OF_ADICIONAL_WAITING + 100) / 100)))
                countdown_timer(waiting_time)
                print("")
                virtual_gang = True
            driver.refresh()
    except KeyboardInterrupt:
        quit_program()
