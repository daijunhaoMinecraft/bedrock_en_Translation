# -*- coding:utf-8 -*-
import json
import threading
from cn_bing_translator import Translator
import wx
from Taowa_wx import *
import requests,os,sys
import logging
from logging import debug

logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.DEBUG)
#重连次数
requests.adapters.DEFAULT_RETRIES = 5
#获取当前执行exe的路径
pathx_pyinstaller = os.path.dirname(os.path.realpath(sys.argv[0]))
#获取当前path路径
pathx = os.path.dirname(os.path.realpath(sys.argv[0]))
#忽略证书警告
requests.packages.urllib3.disable_warnings()
#请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
}

#拖拽文件获取文件路径功能
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            logging.info(f"用户拖拽文件选择文件:{filename}")
            self.window.SetValue(filename)

class Frame(wx_Frame):
    def __init__(self):
        wx_Frame.__init__(self, None, title='Bedrock_LangFiles_Translation(version:0.0.1)', size=(1200, 650),name='frame',style=541072384)
        icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'arqpw-nri9f-001.ico')
        self.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_ICO))
        self.启动窗口 = wx_Panel(self)
        self.Centre()
        self.标签1 = wx_StaticTextL(self.启动窗口, size=(156, 24), pos=(26, 35), label='请输入转换前的语言:',name='staticText', style=1)
        self.标签2 = wx_StaticTextL(self.启动窗口, size=(156, 24), pos=(26, 83), label='请输入转换后的语言:',name='staticText', style=1)
        self.编辑框1 = wx_TextCtrl(self.启动窗口, size=(339, 22), pos=(180, 37), value='en', name='text', style=0)
        self.编辑框2 = wx_TextCtrl(self.启动窗口, size=(339, 22), pos=(180, 85), value='zh-Hans', name='text', style=0)
        self.标签5 = wx_StaticTextL(self.启动窗口, size=(171, 24), pos=(574, 35), label='语言文件路径(lang/json文件):',name='staticText', style=1)
        self.编辑框5 = wx_TextCtrl(self.启动窗口, size=(418, 22), pos=(742, 37), value='', name='text', style=16)
        self.按钮1 = wx_Button(self.启动窗口, size=(80, 32), pos=(574, 68), label='选择文件', name='button')
        self.按钮1.Bind(wx.EVT_BUTTON, self.按钮1_按钮被单击)
        self.超级列表框1 = wx_ListCtrl(self.启动窗口, size=(1134, 316), pos=(26, 201), name='listCtrl', style=8227)
        self.超级列表框1.AppendColumn('对应的默认名称', 0, 225)
        self.超级列表框1.AppendColumn('翻译前的名称', 0, 394)
        self.超级列表框1.AppendColumn('翻译后的名称', 0, 422)
        self.超级列表框1.AppendColumn('转换前的语言', 0, 149)
        self.超级列表框1.AppendColumn('转换后的语言', 0, 164)
        self.按钮2 = wx_Button(self.启动窗口, size=(80, 32), pos=(26, 546), label='保存文件', name='button')
        self.按钮2.Bind(wx.EVT_BUTTON, self.按钮2_按钮被单击)
        self.按钮3 = wx_Button(self.启动窗口, size=(80, 32), pos=(1080, 158), label='开始翻译', name='button')
        self.按钮3.Bind(wx.EVT_BUTTON, self.按钮3_按钮被单击)
        logging.info("初始化框架完成!")

        self.超级链接框1 = wx_adv_HyperlinkCtrl(self.启动窗口, size=(307, 22), pos=(26, 126), name='hyperlink',label='请输入语言代码,可参考微软官方链接(翻译器语言支持)',url='https://learn.microsoft.com/zh-cn/azure/ai-services/translator/language-support',style=1)
        self.多选框1 = wx_CheckBox(self.启动窗口, size=(307, 24), pos=(26, 159), name='check',label='自动检测语言(可能不准确,建议指定语言)', style=16384)
        self.多选框1.Bind(wx.EVT_CHECKBOX, self.多选框1_狀态被改变)

        self.编辑框5.SetDropTarget(MyFileDropTarget(self.编辑框5))
        self.按钮2.Disable()
        self.超级列表框1.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.popup_menu = wx.Menu()
        delete_item = self.popup_menu.Append(-1, '修改')
        self.Bind(wx.EVT_MENU, self.delete_content_can_place_on, delete_item)
        logging.info("程序启动!")
    def is_json(self,content):
        try:
            json.loads(content)
            return True
        except Exception:
            return False

    def delete_content_can_place_on(self,event):
        global get_en_lang_new
        try:
            test_is = get_en_lang_new
        except Exception:
            wx.MessageDialog(self, f'请点击开始翻译并等待翻译完成!', 'Error', wx.OK | wx.ICON_ERROR).ShowModal()
            return
        get_en_lang_new = str(get_en_lang_new)
        logging.info(f"用户选择项:{self.超级列表框1.GetFirstSelected()}")
        if self.超级列表框1.GetFirstSelected() == -1:
            logging.error("用户未选中项!")
            wx.MessageDialog(self, f'请选择一个项!', 'Error', wx.OK | wx.ICON_ERROR).ShowModal()
        else:
            dialog = wx.TextEntryDialog(self, "请输入修改后的内容:", "修改内容", self.超级列表框1.GetItem(self.超级列表框1.GetFirstSelected(), 2).GetText())
            if dialog.ShowModal() == wx.ID_OK:
                user_input = dialog.GetValue()
                logging.info(self.is_json(get_en_lang_new))
                if self.is_json(get_en_lang_new):
                    get_en_lang_new = json.loads(get_en_lang_new)
                    for i in get_en_lang_new:
                        if str(i) == self.超级列表框1.GetItem(self.超级列表框1.GetFirstSelected(), 0).GetText():
                            get_en_lang_new[str(i)] = user_input
                            self.超级列表框1.SetItem(self.超级列表框1.GetFirstSelected(), 2, user_input)
                            get_en_lang_new = json.dumps(get_en_lang_new,ensure_ascii=False,indent=4)
                            break

                else:
                    lines = get_en_lang_new.strip().split('\n')
                    get_content1 = ""
                    for line in lines:
                        key_value = line.split('=')
                        if len(key_value) == 2:
                            key, value = key_value
                            if key == self.超级列表框1.GetItem(self.超级列表框1.GetFirstSelected(), 0).GetText():
                                get_content1 += f"{key}={user_input}\n"
                                self.超级列表框1.SetItem(self.超级列表框1.GetFirstSelected(), 2, user_input)
                            else:
                                get_content1 += f"{line}\n"
                        else:
                            get_content1 += f"{line}\n"
                    get_content1 = get_content1.strip()
                    get_en_lang_new = get_content1.strip()
                wx.MessageDialog(self, f'修改完成!', 'info', wx.OK | wx.ICON_INFORMATION).ShowModal()
            else:
                logging.warning(f"用户取消修改")

    def 按钮1_按钮被单击(self,event):
        # 创建文件选择对话框
        dialog = wx.FileDialog(self, "选择文件(en_US.lang/en_US.json)", "", "en_US.lang", "json files (*.json)|*.json|" "lang files (*.lang)|*.lang|" "All files (*.*)|*.*", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        # 显示对话框
        if dialog.ShowModal() == wx.ID_OK:
            logging.info(f"用户选择文件:{dialog.GetPath()}")
            self.编辑框5.SetValue(dialog.GetPath())


    def 超级列表框1_选中表项(self,event):
        pass


    def 按钮2_按钮被单击(self,event):
        global get_en_lang_new
        try:
            test_is = get_en_lang_new
        except Exception:
            wx.MessageDialog(self, f'请先开始翻译!', 'Error', wx.OK | wx.ICON_ERROR).ShowModal()
            return
        get_en_lang_new = str(get_en_lang_new)
        if self.is_json(get_en_lang_new):
            get_en_lang_new = json.dumps(json.loads(get_en_lang_new),ensure_ascii=False,indent=4)

        dlg = wx.FileDialog(self, message="保存翻译后的文件",defaultFile=f"en_US",wildcard="json Files (*.json)|*.json|" "lang Files (*.lang)|*.lang|" "All files (*.*)|*.*", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            with open(dlg.GetPath(), mode="w", encoding="utf-8") as f:
                f.write(get_en_lang_new)
                f.close()
            save_log_ok = wx.MessageDialog(None, caption="info", message="保存文件成功",style=wx.OK | wx.ICON_INFORMATION)
            if save_log_ok.ShowModal() == wx.ID_OK:
                pass

    def 按钮3_按钮被单击(self,event):
        threading.Thread(target=self.按钮3_按钮被单击_1).start()

    def 按钮3_按钮被单击_1(self):
        global get_en_lang_new
        if self.多选框1.GetValue() == True:
            if self.编辑框2.GetValue() == "" or self.编辑框5.GetValue() == "":
                wx.MessageDialog(self, f'请确保每一项值都不为空!', 'Error', wx.OK | wx.ICON_ERROR).ShowModal()
                self.按钮3.Enable()
                self.按钮2.Enable()
                return
        elif self.多选框1.GetValue() == False:
            if self.编辑框1.GetValue() == "" or self.编辑框2.GetValue() == "" or self.编辑框5.GetValue() == "":
                wx.MessageDialog(self, f'请确保每一项值都不为空!', 'Error', wx.OK | wx.ICON_ERROR).ShowModal()
                self.按钮3.Enable()
                self.按钮2.Enable()
                return
        try:
            with open(self.编辑框5.GetValue(),"r",encoding='utf-8') as f:
                get_en_lang = f.read()
                f.close()
        except Exception:
            wx.MessageDialog(self, f'请选择正确的文件!', 'Error', wx.OK | wx.ICON_ERROR).ShowModal()
            self.按钮3.Enable()
            self.按钮2.Enable()
            return
        self.超级列表框1.DeleteAllItems()
        self.按钮3.Disable()
        self.按钮2.Disable()
        translator = Translator()
        if self.is_json(get_en_lang):
            get_en_lang = json.loads(get_en_lang)
            for json_key in get_en_lang:
                try:
                    json_value = get_en_lang[json_key]
                    fromLang = self.编辑框1.GetValue()
                    if self.多选框1.GetValue() == True:
                        fromLang = "auto-detect"
                    toLang = self.编辑框2.GetValue()
                    add_content_Lang = ""
                    if fromLang == "auto-detect":
                        add_content_Lang = "(自动检测语言)"
                    get_content = translator.process(json_value, fromLang=fromLang, toLang=toLang)
                    logging.info(f"翻译前的结果:{json_value},翻译后的结果:{get_content}")
                    get_en_lang[json_key] = get_content
                    self.超级列表框1.Append([json_key, json_value, get_content, fromLang + add_content_Lang, toLang])
                except Exception as e:
                    logging.error(f"出现错误:{e}")
                    wx.MessageDialog(self, f'翻译出现错误,请检查是否是正确的语言或网络问题!', 'Error',wx.OK | wx.ICON_ERROR).ShowModal()
                    self.按钮3.Enable()
                    self.按钮2.Enable()
                    return
            get_en_lang_new = json.dumps(get_en_lang,ensure_ascii=False,indent=4)
        else:
            # 按等号分割每一行，创建键值对列表
            lines = get_en_lang.strip().split('\n')
            get_content1 = ""
            for line in lines:
                key_value = line.split('=')
                if len(key_value) == 2:
                    key, value = key_value
                    try:
                        fromLang = self.编辑框1.GetValue()
                        if self.多选框1.GetValue() == True:
                            fromLang = "auto-detect"
                        toLang = self.编辑框2.GetValue()
                        add_content_Lang = ""
                        if fromLang == "auto-detect":
                            add_content_Lang = "(自动检测语言)"
                        get_content = translator.process(value.strip(),fromLang=fromLang,toLang=toLang)
                        logging.info(f"翻译前的结果:{value.strip()},翻译后的结果:{value.strip()}")
                        self.超级列表框1.Append([key.strip(),value.strip(),get_content,fromLang+add_content_Lang,toLang])
                        get_content1 += f'{key}={get_content}\n'
                    except Exception as e:
                        logging.error(f"出现错误:{e}")
                        wx.MessageDialog(self, f'翻译出现错误,请检查是否是正确的语言或网络问题!', 'Error',wx.OK | wx.ICON_ERROR).ShowModal()
                        self.按钮3.Enable()
                        self.按钮2.Enable()
                        return
                else:
                    get_content1 += f"{line}\n"
            get_content1 = get_content1.strip()
            get_en_lang_new = get_content1

        self.按钮3.Enable()
        self.按钮2.Enable()
        wx.MessageDialog(self, f'翻译完成,共计翻译了{str(self.超级列表框1.GetItemCount())}个条目!', 'info',wx.OK | wx.ICON_INFORMATION).ShowModal()
    def on_right_click(self,event):
        pos = wx.GetMousePosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.popup_menu, pos)

    def 多选框1_狀态被改变(self,event):
        if self.多选框1.GetValue() == True:
            self.编辑框1.Disable()
        elif self.多选框1.GetValue() == False:
            self.编辑框1.Enable()

class myApp(wx.App):
    def  OnInit(self):
        self.frame = Frame()
        self.frame.Show(True)
        return True

if __name__ == '__main__':
    app = myApp()
    app.MainLoop()