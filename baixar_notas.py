import os
import time
import glob
import getpass
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains # <-- NOVA IMPORTAÇÃO PARA O RATO
from dotenv import load_dotenv
load_dotenv()  # lê o .env local (não vai para o GitHub)

# ================= CONFIGURAÇÕES =================
DIRETORIO_BASE = os.getenv("DIRETORIO_BASE") 
TEMPO_ESPERA_CERTIFICADO_INICIAL = 15 
# =================================================

def configurar_navegador(pasta_download):
    edge_options = Options()
    usuario_windows = getpass.getuser()
    caminho_perfil = os.getenv("CAMINHO_PERFIL_EDGE", rf"C:\Users\{usuario_windows}\AppData\Local\Microsoft\Edge\User Data")
    edge_options.add_argument(f"user-data-dir={caminho_perfil}")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    prefs = {
        "download.default_directory": pasta_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    edge_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Edge(options=edge_options)
    driver.maximize_window()
    return driver

def processar_csvs():
    arquivos_csv = glob.glob(os.path.join(DIRETORIO_BASE, "*.csv"))
    
    if not arquivos_csv:
        print(f"ERRO: Nenhum CSV encontrado em: {DIRETORIO_BASE}")
        return

    primeira_execucao = True

    for arquivo in arquivos_csv:
        nome_arquivo = os.path.basename(arquivo).lower()
        tipo = "Dest" if 'dest' in nome_arquivo else "Emit" if 'emit' in nome_arquivo else "Outros"
        pasta_destino = os.path.join(DIRETORIO_BASE, f"XMLs_{tipo}")
        os.makedirs(pasta_destino, exist_ok=True)
        
        print(f"\n" + "="*40)
        print(f">>> A ler ficheiro: {nome_arquivo}")
        print("="*40)
        
        driver = configurar_navegador(pasta_destino)
        # Aumentei para 120 segundos para lhe dar tempo de sobra caso precise de resolver as imagens manualmente
        wait_longo = WebDriverWait(driver, 120) 
        wait_curto = WebDriverWait(driver, 10)

        try:
            df = pd.read_csv(arquivo, sep=';', dtype=str)
            df.columns = df.columns.str.strip()
            
            for index, row in df.iterrows():
                situacao = str(row.get('Situacao', '')).strip().upper()
                chave = str(row.get('Chave de Acesso', '')).replace("'", "").strip()
                
                if chave == 'nan' or len(chave) != 44: continue
                if 'CANCELADA' in situacao:
                    print(f"[{index+1}] ⏭️ A saltar nota CANCELADA: {chave}")
                    continue

                print(f"\n[{index+1}] 🔍 A consultar chave: {chave}")
                
                driver.get("https://www.fsist.com.br/")
                time.sleep(2) 

                try:
                    # 1. Preenche e envia a chave
                    campo_chave = wait_curto.until(EC.element_to_be_clickable((By.ID, "chave")))
                    campo_chave.click()
                    time.sleep(0.5)
                    campo_chave.clear()
                    campo_chave.send_keys(chave)
                    time.sleep(0.5)
                    campo_chave.send_keys(Keys.ENTER)
                    
                    time.sleep(3) # Tempo para o Captcha carregar no ecrã

                    # ========================================================
                    # TENTATIVA DE CLICAR NO CAPTCHA COM O "RATO FÍSICO"
                    # ========================================================
                    try:
                        # Procura o iframe (a janela embutida) do CAPTCHA
                        iframes = driver.find_elements(By.XPATH, "//iframe[contains(@title, 'reCAPTCHA') or contains(@title, 'hCaptcha')]")
                        if iframes:
                            print("   -> 🤖 CAPTCHA detetado! A simular o rato humano para clicar...")
                            driver.switch_to.frame(iframes[0])
                            
                            # Encontra o quadrado
                            checkbox = wait_curto.until(EC.element_to_be_clickable((By.ID, "checkbox") or (By.CLASS_NAME, "recaptcha-checkbox-border")))
                            
                            # Usa o ActionChains para mover o rato até lá e clicar
                            acoes = ActionChains(driver)
                            acoes.move_to_element(checkbox).click().perform()
                            
                            print("   -> 🤞 Cliquei! (Se pedir imagens, resolva no ecrã)")
                            
                            driver.switch_to.default_content()
                    except Exception as e:
                        driver.switch_to.default_content()
                        pass
                    # ========================================================

                    if primeira_execucao:
                        print(f"   -> ⚠️ Atenção: Se pedir o CERTIFICADO, selecione-o agora! ({TEMPO_ESPERA_CERTIFICADO_INICIAL}s)")
                        time.sleep(TEMPO_ESPERA_CERTIFICADO_INICIAL)
                        primeira_execucao = False
                    
                    # 2. Aguarda a libertação do download no site
                    print("   -> ⏳ A aguardar libertação do botão de download (resolva o Captcha se necessário)...")
                    btn_xpath = "//a[contains(., 'Download XML')] | //button[contains(., 'Download XML')] | //*[contains(@class, 'download') and contains(., 'XML')]"
                    
                    botao_download = wait_longo.until(EC.presence_of_element_located((By.XPATH, btn_xpath)))
                    driver.execute_script("arguments[0].click();", botao_download)
                    
                    print("   -> ✅ Download XML efetuado com sucesso!")
                    time.sleep(3) 
                    
                except Exception as e:
                    print(f"   -> ❌ AVISO: Tempo esgotado (120s) ou erro na chave {chave}.")
                    
        except Exception as e:
            print(f"ERRO ao processar ficheiro: {e}")
        finally:
            driver.quit()

    print("\n🎉 PROCESSO FINALIZADO!")

if __name__ == "__main__":
    processar_csvs()