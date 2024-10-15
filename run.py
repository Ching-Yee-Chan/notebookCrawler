import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.edge.options import Options
import win32gui
import win32con
from concurrent.futures import ThreadPoolExecutor
import os
import argparse
import random

mutex = threading.Lock()

def process_pdf(pdf_path, driver):
    driver.get('https://notebooklm.google.com')
    while True:
        time.sleep(1)
        try:
            # 找到并点击“新建笔记本”按钮
            try:
                new_notebook_button = driver.find_element(By.CLASS_NAME, "create-button")
            except:
                new_notebook_button = driver.find_element(By.CLASS_NAME, "project-button__new")
            new_notebook_button.click()
            # 等待页面加载完成
            time.sleep(3)
            # 找到并点击上传来源按钮
            upload_button = driver.find_element(By.XPATH, "//button[@aria-label='从计算机上传来源']")
            time.sleep(3)
            break
        except:
            driver.get('https://notebooklm.google.com')
            continue

    # 使用锁来确保每次只有一个线程进入这段代码
    # TODO: 把win32gui换成macOS的库，或者直接换成输网址
    with mutex:
        while True:
            upload_button = driver.find_element(By.XPATH, "//button[@aria-label='从计算机上传来源']")
            upload_button.click()
            time.sleep(2)
            if win32gui.FindWindow('#32770', u'打开') > 0:
                break
            else:
                driver.refresh()
                time.sleep(3)

        # 上传PDF
        dialog = win32gui.FindWindow('#32770', u'打开')  # 对话框
        ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None) 
        ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
        Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)  # 上面三句依次寻找对象，直到找到输入框Edit对象的句柄
        button_left = win32gui.FindWindowEx(dialog, 0, 'Button', None)  # 确定按钮Button
        button_middle = win32gui.FindWindowEx(dialog, button_left, 'Button', None)  # 找到右边的按钮

        win32gui.SendMessage(Edit, win32con.WM_SETTEXT, None, pdf_path)  # 往输入框输入绝对地址
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button_middle)  # 按button

    # 轮询点击生成对话按钮
    while True:
        while True:
            try:
                # generate_button = driver.find_element(By.XPATH, "/html/body/labs-tailwind-root/div/notebook/div/div[2]/div/div/div[2]/chat-layout/div/omnibar/div[1]/notebook-guide/div/div[2]/div[1]/div[2]/div[2]/audio-overview/div/div/div[2]/button")
                generate_button = driver.find_element(By.XPATH, "//audio-overview/div/div/div[2]/button")
                break
            except:
                random.random()
                # time.sleep(3)
                random_sleep = random.uniform(3, 5)
                time.sleep(random_sleep)
                continue
        generate_button.click()
        # time.sleep(3)
        random_sleep = random.uniform(3, 5)
        time.sleep(random_sleep)

        while True:
            try:
                retry_button = driver.find_element(By.XPATH, "//audio-overview/div/div/div[3]/button")
                retry_button.click()
                # time.sleep(3)
                random_sleep = random.uniform(3, 5)
                time.sleep(random_sleep)
            except:
                break
        
        # 如果不再弹出生成按钮了，那就成功了
        try:
            generate_button = driver.find_element(By.XPATH, "//audio-overview/div/div/div[2]/button")
        except:
            break
    

    # 修改notebook的名称
    notebook_name = os.path.basename(pdf_path).replace('.pdf', '')
    name_box = driver.find_element(By.XPATH, "//input[@class='title-input ng-untouched ng-pristine ng-valid']")
    name_box.clear()
    name_box.send_keys(notebook_name)
    name_box.send_keys('\n')

    # 轮询检查是否生成完成
    while True:
        try:
            generating_element = driver.find_element(By.XPATH, "//span[text()='正在生成对话…']")
            time.sleep(10)
        except:
            break

    # 下载音频
    dot_button = driver.find_element(By.XPATH, "//button[@aria-label='查看音频播放器的更多选项']")
    dot_button.click()
    time.sleep(1)
    # Size会因不同浏览器变化，需要搜索
    size = 1
    while True:
        try:
            download_button = driver.find_element(By.XPATH, f"//*[@id='mat-menu-panel-{size}']/div/a")
            download_button.click()
            break
        except:
            size = size + 1 if size < 100 else 1
            time.sleep(0.5)
            continue
    time.sleep(2)
    back_button = driver.find_element(By.CLASS_NAME, "side-panel-toggle")
    back_button.click()
    time.sleep(2)


def process_pdf_list(pdf_list, rank, start_port):
    # 连接到已登录的窗口
    options = Options()
    options.debugger_address = "127.0.0.1:" + str(start_port + rank)
    # TODO: 改成webdriver.Firefox
    driver = webdriver.Edge(options=options)

    for pdf_path in pdf_list:
        print(f"Thread {rank} processing {pdf_path}")
        process_pdf(pdf_path, driver)
        print(f"Thread {rank} processed {pdf_path}")

    driver.quit()

def delete_notebooks(start_port):
    # 连接到已登录的窗口
    options = Options()
    options.debugger_address = "127.0.0.1:" + str(start_port)
    # TODO: 改成webdriver.Firefox
    driver = webdriver.Edge(options=options)

    while True:
        driver.get('https://notebooklm.google.com')
        time.sleep(1)
        # 找到并点击项目操作菜单按钮
        try:
            project_actions_menu_button = driver.find_element(By.XPATH, "/html/body/labs-tailwind-root/div/welcome-page/div/div[1]/div/project-button[2]/mat-card/div[1]/project-action-button/button")
        except:
            break
        project_actions_menu_button.click()
        time.sleep(1)

        # 找到并点击删除按钮
        delete_button = driver.find_element(By.XPATH, "//button[.//mat-icon[text()='delete'] and contains(@class, 'project-button-hamburger-menu-action')]")
        delete_button.click()
        time.sleep(1)

        # 确认删除
        confirm_delete_button = driver.find_element(By.XPATH, "//button[@aria-label='确认删除']")
        confirm_delete_button.click()
        time.sleep(3)

def get_pdf_files(directory):
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def main(args):
    pdf_root = args.pdf_root
    num_threads = args.num_threads
    start_port = args.start_port

    # List of PDF files to process
    pdf_files = get_pdf_files(pdf_root)

    # Split the list of PDF files into chunks for each thread
    pdf_chunks = [pdf_files[i::num_threads] for i in range(num_threads)]
    print(f"Processing {len(pdf_files)} PDF files using {num_threads} threads")

    # Use ThreadPoolExecutor to process PDF lists concurrently
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_pdf_list, pdf_chunks[i], i, start_port) for i in range(num_threads)]
        for future in futures:
            future.result()
    
    # Delete all notebooks
    delete_notebooks(start_port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process PDF files and generate audios using Google NotebookLM')
    parser.add_argument('--pdf_root', type=str, required=True, help='Root directory containing PDF files')
    parser.add_argument('--num_threads', type=int, default=1, help='Number of threads to use')
    parser.add_argument('--start_port', type=int, default=9001, help='Starting port number for WebDriver debugging')
    args = parser.parse_args()
    main(args)
