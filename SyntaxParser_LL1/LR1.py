import re
import tkinter as tk
from tkinter import ttk
import pygraphviz as pgv
from PIL import Image, ImageTk
#项目集
class Entryset:
    def __init__(self):
        self.entryset=[]
        self.nextdic={}#跳转项目集,存放在s中的下标
    def __eq__(self, other):
            if isinstance(other, Entryset):
                res=True
                temp=[item[0] for item in self.entryset]
                for entry in other.entryset:
                    if entry[0] not in temp:
                        return False
            return True
class LALR1:
    def __init__(self,grammar_list):
        self.grammar_list=grammar_list
        self.start_ch=None
        self.broaden()
        self.VN=sorted(self.getVN())
        self.VT=sorted(self.getVT())
        self.grammar_dic=self.list_to_dict()     
        self.First=self.FIRST()
        self.s=[]
        self.calEntryFamily()
        self.drawEntryFamily()
        print(self.First)
        print(self.VN)
        print(self.VT)
    #将文法拓广
    def broaden(self):
        #获得原始开始符
        ch = self.grammar_list[0][0]
        self.start_ch=ch+'\''
        s=self.start_ch+'->'+ch
        self.grammar_list=[s]+self.grammar_list   
    #将文法列表转换成字典
    def list_to_dict(self):
        dic={}
        for key in self.VN:
            dic[key]=[]
            
        for s in self.grammar_list:
            List=s.split('->')
            List2=[s.split('|') for s in List[1:]]
            dic[List[0]]=sum(List2,dic[List[0]])
        return dic
    #获取非终结符集合
    def getVN(self):
        VN=[]
        for s in self.grammar_list:
            VN.append(s.split('->')[0])
        return list(set(VN))
    #获取终结符集合
    def getVT(self):
        VN=self.getVN()
        newList=[s.split('->')[1] for s in self.grammar_list]
        gl_str=''.join(s for s in newList)
        VT=list(set(ch for ch in gl_str if (ch not in VN)and(ch !='|')))
        return VT
    #求任意句型的First集合
    def getFIRST(self,rp):
        if (rp[0] in self.VT )or(rp[0]=='#'):
            return set(rp[0])
        elif rp[0] in self.VN:
            if 'ε' not in self.First[rp[0]]:
                return self.First[rp[0]]
            else:
                result_set=set()
                i=0
                for ch in rp:
                    if 'ε' in self.First[ch]:
                        result_set.update(self.First[ch].difference({'ε'}))
                    else:
                        result_set.update(self.First[ch])
                        break
                    i=i+1
                if ('ε' in self.First[rp[-1]])and(i==len(rp)-1):
                    result_set.add('ε') 
                return result_set                                                              
    #求FIRST集合
    def getFirst(self,v,first):
        for it in self.grammar_dic[v]:
            epsilon=1
            for ch in it:
                if ch in self.VT:#如果是非终结符
                    first[v].add(ch)
                    epsilon=0
                    break
                elif ch==v:
                    epsilon=0
                    break
                else:
                    self.getFirst(ch,first)#将FIRST(ch)\'ε'放入
                    if 'ε' in first[ch]:
                        first[v].update(first[ch].difference({'ε'}))
                    else:first[v].update(first[ch])
                    
                    if 'ε' not in first[ch]:#如果FIRST(ch)不含'ε'，继续看下一个字符的FIRST
                        epsilon=epsilon and 0
                        break
                    else:epsilon=epsilon and 1
            if epsilon:first[v].add('ε')    #如果FIRST(产生式右部)含有'ε'，将'ε'放入                                          
    #求FIRST集合         
    def FIRST(self):
        first={}
        for vn in self.VN:
            first[vn]=set()
        
        for vn in self.VN:
            self.getFirst(vn,first)
        
        return first
    #求项目集族
    def calEntryFamily(self):
        entry_dic={}
        for k in self.grammar_dic:
            entry_dic[k]=[]
            for item in self.grammar_dic[k]:
                for i in range(0,len(item)+1):
                    s=item[0:i]+'·'+item[i:]
                    entry_dic[k].append(s)
        
        s0=Entryset()
        #获取一下开始符
        ch=self.grammar_list[0].split('->')[0]
        #求第一个项目集
        s0.entryset.append((ch+'->'+entry_dic[ch][0],('#',)))
        self.CLOSURE(s0,entry_dic)
        self.s.append(s0)
        
        #获取一下所有的字符
        temp_list=self.VN.copy()
        temp_list.remove(self.start_ch)
        ch_str=''.join(c for c in temp_list)+''.join(c for c in self.VT)
        #创建集族
        for S in self.s:
            for ch in ch_str:
                entryset=self.calEntry(S,ch)
                if entryset:
                    newS=Entryset()
                    newS.entryset=entryset
                    self.CLOSURE(newS,entry_dic)
                    if newS not in self.s:
                        self.s.append(newS)
                        S.nextdic[ch]=len(self.s)-1
                    else:
                        x=self.s.index(newS)
                        self.sumEntry(self.s[x],newS.entryset)
                        S.nextdic[ch]=x                                            
    #求一个项目集,通过移进字符      
    def calEntry(self,S,ch):
        res=[]
        for entry in S.entryset:
            rule=entry[0]
            x=rule.index('·')
            if x!=len(rule)-1 and rule[x+1]==ch:
                new_rule=rule[0:x]+ch+'·'+rule[x+2:]
                new_entry=(new_rule,entry[1])
                res.append(new_entry)
        if len(res)==0:
            return None
        else:
            return res     
    #闭包运算        
    def CLOSURE(self,S,entry_dic):
        #先将项目集拓展开
        pattern0=re.compile(r'.·[A-Z]')#匹配待约项目
        pattern1 = re.compile(r'^·')#匹配·位于最左边的情况
        
        #将待约项目放进项目集中
        i=0
        entryList=S.entryset
        while(i<len(entryList)):
            entry=entryList[i]
            if re.search(pattern0,entry[0]):
                x=entry[0].index('·')
                List=entry_dic[entry[0][x+1]]
                for item in List:
                    if re.match(pattern1,item):
                        expect_ch=self.getExpect(entry)    
                        t=(entry[0][x+1]+'->'+item,expect_ch)
                        if t not in entryList:
                            entryList.append(t)
            i+=1
        self.sumEntry(S,entryList)
    #合并项目
    def sumEntry(self,S,entryList):
        entrydic={}
        for entry in S.entryset:
            entrydic[entry[0]]=entry[1]
        for entry in entryList:
            k=entry[0]
            v=entry[1]
            entrydic[k]=tuple(set(list(entrydic[k])+list(v)))
                 
        S.entryset=list(entrydic.items())     
    #获取展望字符        
    def getExpect(self,entry):
        result=set()
        x=entry[0].index('·')
        for ch in entry[1]:
            rest=entry[0][x+2:]+ch
            result=result|self.getFIRST(rest)
        return tuple(result)            
    #GOTO函数
    def GO(self,S,a):
        #传入起点状态和字符，返回目标状态在s中的下标
        return S.nextdic[a]
    #生成分析表
    def analyzed_tab(self):
        self.analyzed_dic={}
        
        temp_list=self.VN.copy()
        temp_list.remove(self.start_ch)
        ch_str=''.join(c for c in self.VT)+'#'+''.join(c for c in temp_list)
        
        #移进项目
        regex_pattern='|'.join(re.escape(ch) for ch in self.VT)
        pattern0=re.compile(r'.·[{}]'.format(regex_pattern))
        #规约项目
        pattern1=re.compile(r'·$')
        #待规约项目
        regex_pattern='|'.join(re.escape(ch) for ch in temp_list)
        pattern2=re.compile(r'.·[{}]'.format(regex_pattern))
        
        for state in self.s:
            dic_List=['' for i in range(0,len(ch_str))]
            List0=[]
            List1=[]
            List2=[]
            for entry in state.entryset:
                if pattern0.search(entry[0]):
                    List0.append(entry)
                elif pattern1.search(entry[0]):
                    List1.append(entry)
                elif pattern2.search(entry[0]):
                    List2.append(entry)
            
            if len(List0)>0:
                for entry in List0:
                    y=entry[0].index('·')
                    ch=entry[0][y+1]
                    j=self.GO(state,ch)
                    dic_List[ch_str.index(ch)]+='s'+str(j)
            if len(List1)>0:
                for entry in List1:
                    rule=entry[0].replace('·','')
                    if rule==self.grammar_list[0]:#如果是接受项目
                        dic_List[ch_str.index('#')]='acc'
                        continue
                    j=self.grammar_list.index(rule)
                    for ch in entry[1]:
                        dic_List[ch_str.index(ch)]='r'+str(j)
            if len(List2)>0:
                for entry in List2:
                    y=entry[0].index('·')
                    ch=entry[0][y+1]
                    j=self.GO(state,ch)
                    dic_List[ch_str.index(ch)]=str(j)
            
            x=self.s.index(state)
            self.analyzed_dic[x]=dic_List
        global Frame2
        analyzed_tree=ttk.Treeview(Frame2)
        columns_name=['状态']
        columns_name.extend([ch for ch in ch_str])
        analyzed_tree['columns']=columns_name
        analyzed_tree.column('#0',width=0,stretch=tk.NO)
        for ch in columns_name:
            analyzed_tree.column(ch,width=2,anchor="center")
            analyzed_tree.heading(ch,text=ch)           
        analyzed_tree.pack(fill=tk.BOTH,expand=True)
        
        for i in range(0,len(self.s)):
            value=[i]
            value.extend(self.analyzed_dic[i])
            analyzed_tree.insert('',tk.END,values=value)                                  
    #分析过程
    def analyze(self,string):
        string+='#'
        state_List=[0]
        ch_List=['#']
        date=[]
        temp_list=self.VN.copy()
        temp_list.remove(self.start_ch)
        ch_str=''.join(c for c in self.VT)+'#'+''.join(c for c in temp_list)
        
        i=0
        step=1
        while i<len(string):
            ch=string[i]
            x=ch_str.index(ch)
            current_state=state_List[-1]
            action=self.analyzed_dic[current_state][x]
            
            if action=='':
                item=[step,''.join(str(s) for s in state_List),''.join(ch for ch in ch_List),string[i:],'ERROR']
                date.append(item)
                break
            #移进
            elif action[0]=='s':
                item=[step,''.join(str(s) for s in state_List),''.join(ch for ch in ch_List),string[i:],f'ACTION[{current_state},{ch}]={action},状态 {action[1]} 入栈 ']
                date.append(item)
                state_List.append(int(action[1]))
                ch_List.append(string[i])
                i+=1
            #规约
            elif action[0]=='r':
                rule=self.grammar_list[int(action[1])]
                item=[step,''.join(str(s) for s in state_List),''.join(ch for ch in ch_List),string[i:]]
                rest_ch=rule.split('->')[1]
                for ch in rest_ch:
                    del(ch_List[-1])
                    del(state_List[-1])
                ch_List.append(rule[0])
                current_state=state_List[-1]
                new_state=self.analyzed_dic[current_state][ch_str.index(rule[0])]
                state_List.append(int(new_state))
                item.append(f'{action}: {rule} 归约,GOTO({current_state},{rule[0]})={new_state} 入栈')
                date.append(item)
            elif action=='acc':
                item=[step,''.join(str(s) for s in state_List),''.join(ch for ch in ch_List),string[i:],'acc:分析成功']
                date.append(item)
                break
            step+=1           
        return date     
    #画LR1项目集族
    def drawEntryFamily(self):
        #创建图形对象
        G = pgv.AGraph(strict=False, directed=True)
        #创建项目集
        for state in self.s:
            x=self.s.index(state)
            G.add_node('I{}'.format(x), label=f'I{x}\n'+'\n'.join(entry[0]+','+str(entry[1]) for entry in state.entryset), shape='rectangle')
        
        #指定节点边关系
        for state in self.s:
            x=self.s.index(state)
            for k,v in state.nextdic.items():
                G.add_edge(f'I{x}',f'I{v}',label=k)
        
        # 设置图形布局
        G.layout(prog='dot',args='-Grankdir=LR')

        # 渲染并保存图片
        G.draw('project_sets.png')                       
#按钮槽函数
def func():
    global l,tree,Entry
    input_text=Entry.get()
    date=l.analyze(input_text)
    tree.delete(*tree.get_children())
    for item in date:
            tree.insert('',tk.END,values=item)   
def createPicTab():
    global notebook, root, image_label,tab2
    if len(notebook.tabs())==2:
        notebook.select(tab2)
        return
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text='项目集族图')
    # 加载图片
    original_image = Image.open('project_sets.png')
    image_width, image_height = original_image.size
    
    # 获取容器的大小
    tab_width = notebook.winfo_width() - 20
    tab_height = notebook.winfo_height() - 20

    # 计算缩放比例
    scale_x = tab_width / image_width
    scale_y = tab_height / image_height
    scale = min(scale_x, scale_y)

    # 调整图片大小
    new_width = int(scale * image_width)
    new_height = int(scale * image_height)
    resized_image = original_image.resize((new_width, new_height),resample=Image.BICUBIC)

    # 将图像转换为 PhotoImage 对象
    photo_image = ImageTk.PhotoImage(resized_image)

    # 在标签中显示图片并使用 place 布局管理器调整大小
    image_label = tk.Label(tab2, image=photo_image)
    image_label.image = photo_image  # 保持对PhotoImage对象的引用
    image_label.place(x=10, y=10, width=new_width, height=new_height)

    # 更新当前选定的标签页
    notebook.select(tab2)         
if __name__=='__main__':
    grammar_list=['S->BB',
              'B->aB',
              'B->b']
    #这个文法的语言是a*ba*b   
    l=LALR1(grammar_list)
    
    root=tk.Tk()
    root.title("LALR(1)语法分析器")
    root.geometry('1000x600')
    root.geometry('+280+100')
    root.resizable(False,False)
    
    notebook = ttk.Notebook(root)
    tab1=tk.Frame(root)
    #————————————————————————————窗口布局——————————————————————————————#
    #放输入框、分析表、按钮控件等
    Frame0=tk.Frame(tab1)
    Frame0.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)
    #放分析栈
    Frame1=tk.Frame(tab1)
    Frame1.pack(fill=tk.BOTH,expand=True,side=tk.RIGHT)
    #————————————————————————————控件布局——————————————————————————————#
    #放分析表
    Frame2=tk.Frame(Frame0)
    Frame2.pack(fill=tk.BOTH,expand=True,side=tk.BOTTOM)
    l.analyzed_tab()
    
    #放输入框、按钮控件等
    Frame3=tk.Frame(Frame0)
    Frame3.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
    
    Frame4=tk.Frame(Frame3,border=0)
    Frame4.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
    Entry=ttk.Entry(Frame4)
    # 定义默认文字
    default_text = "请输入待分析串"
    # 插入默认文字
    Entry.insert(0, default_text)
    # 绑定事件，当输入框获得焦点时，清空默认文字
    def clear_default_text(event):
        if Entry.get() == default_text:
            Entry.delete(0, tk.END)

    def restore_default_text(event):
        if not Entry.get():
            Entry.insert(0, default_text)

    Entry.bind("<FocusIn>", clear_default_text)
    Entry.bind("<FocusOut>", restore_default_text)
    
    Entry.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)
    button=ttk.Button(Frame4,text="确定",command=func)
    button.pack(fill=tk.BOTH,expand=True,side=tk.RIGHT)
    
    Frame5=tk.Frame(Frame3)
    Frame5.pack(fill=tk.BOTH,expand=True,side=tk.BOTTOM)
    button2=ttk.Button(Frame5,text='查看LALR(1)项目集族',command=createPicTab)
    button2.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
    LR1_Text=tk.Text(Frame5,height=10,width=50)
    LR1_Text.pack(fill=tk.BOTH,expand=True,side=tk.BOTTOM)
    #展示文法
    LR1_Text.config(state=tk.NORMAL)
    LR1_Text.insert(tk.END,"\n".join(l.grammar_list))
    LR1_Text.config(state=tk.DISABLED)
    
    #分析栈展示
    scrollbar=tk.Scrollbar(Frame1)
    scrollbar.pack(fill=tk.Y,side=tk.RIGHT)
    global tree
    tree=ttk.Treeview(Frame1,yscrollcommand=scrollbar.set)
    
    tree['columns']=('步骤',"状态栈",'符号栈',"输入串","动作说明")
    tree.column('#0',width=0,stretch=tk.NO)
    tree.column('步骤',width=20)
    tree.column("状态栈",width=50)
    tree.column('符号栈',width=50)
    tree.column("输入串",width=50)
    tree.column("动作说明",width=200)
    
    tree.heading('步骤',text='步骤')
    tree.heading("状态栈",text="状态栈")
    tree.heading('符号栈',text='符号栈')
    tree.heading("输入串",text="输入串")
    tree.heading("动作说明",text="动作说明")   
         
    scrollbar.config(command=tree.yview)
    tree.pack(fill=tk.BOTH,expand=True)
    
    notebook.add(tab1, text="主界面")
    notebook.pack(padx=10, pady=10, fill="both", expand=True)
    
    tk.mainloop()
    try:
        root.destroy()
    except tk.TclError as e:
        print("窗口已经销毁")