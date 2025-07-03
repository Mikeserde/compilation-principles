import re
import copy
import tkinter as tk
from tkinter import ttk
import sys
class LL1:
    def __init__(self,grammar_list):
        global grammarText,LL1Text
        
        self.grammar_list=grammar_list
        self.VN=sorted(self.getVN())
        self.VT=sorted(self.getVT())
        self.grammar_dic=self.list_to_dict()
        if self.is_left_recursion():
           print("文法存在左递归，请修改。") 
        else:    
            self.First=self.FIRST()
            self.Follow=self.FOLLOW()
            self.LL1_dic=self.get_LL1_dic()
        
    def is_left_recursion(self):
        for k in self.grammar_dic:
            for item in self.grammar_dic[k]:
                if k==item[0]:
                    return True
        return False

    #将文法列表转换成字典
    def list_to_dict(self):
        dic={}
        for key in self.VN:
            dic[key]=[]
            
        for s in self.grammar_list:
            List=s.split('->')
            List2=[s.split('|') for s in list(set(List)-set(self.VN))]
            dic[List[0]]=sum(List2,dic[List[0]])
        return dic
           
    # 获取非终结符集合
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
    
    def getFIRST(self,rp):
        if rp[0] in self.VT:
            return set(rp[0])
        elif rp[0] in self.VN:
            if 'ε' not in self.First[rp[0]]:
                return self.First[rp[0]]
            else:
                return self.First[rp[0]].difference({'ε'}).update(self.First[rp[1]])
                     
    #求FIRST集合
    def getFirst(self,v,first):
        for it in self.grammar_dic[v]:
            epsilon=1
            for ch in it:
                if ch in self.VT:#如果是非终结符
                    first[v].add(ch)
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
                
    def FIRST(self):
        first={}
        for vn in self.VN:
            first[vn]=set()
        
        for vn in self.VN:
            self.getFirst(vn,first)
        
        return first

    #求FOLLOW集合
    def getFollow(self,v,follow):
        regex_pattern0='|'.join(re.escape(ch) for ch in self.VT)#所有终结符
        regex_pattern1='|'.join(re.escape(ch) for ch in self.VN)#所有非终结符
        pattern=re.compile(r'^[{0}]*[{1}]{{2}}'.format(regex_pattern0,regex_pattern1))#识别形如BC情况
        pattern1=re.compile(r'[{1}][{0}]$'.format(regex_pattern0,regex_pattern1))#识别形如Ab的情况
        for ch in self.grammar_dic[v]:#对每个非终结符进行求解FOLLOW集
                if pattern.match(ch):#如果满足BC情况
                    pattern2=re.compile(r'^[{}]*'.format(regex_pattern0))#去除终结符前缀
                    string=pattern2.sub('',ch)
                    follow[string[1]].update(follow[v])
                    if 'ε' in self.First[string[1]]:#处理First集带有空字符的情况
                        follow[string[0]].update(self.First[string[1]].difference({'ε'}))
                        follow[string[0]].update(follow[v])
                    else:
                        follow[string[0]].update(self.First[string[1]])
                elif pattern1.search(ch):#如果满足Ab情况
                    follow[ch[-2]].add(ch[-1]) 
                                   
    def FOLLOW(self):
        follow={}
        for vn in self.VN:
            follow[vn]=set()
        follow['E'].add('#')
        for vn in self.VN:
            self.getFollow(vn,follow)
        
        for vn in self.VN:
            self.getFollow(vn,follow)
            
        return follow
    
    def get_LL1_dic(self):
        dic={}
        for k in self.grammar_dic:
            List=copy.deepcopy(self.VT)
            List[-1]='#'
            mark=[0]*len(List)
            for it in self.grammar_dic[k]:
                for i in self.VT[0:-1]:
                    if i in self.getFIRST(it):                        
                        mark[List.index(i)]=1
                        List[List.index(i)]=it
                if 'ε' in self.getFIRST(it):
                    for i in self.Follow[k]:
                            mark[List.index(i)]=1
                            List[List.index(i)]=it
            for i in range(len(mark)):
                if mark[i]==0:
                    List[i]='ERR'
            dic[k]=List
        return dic                   
        
    def LL1_analyze(self,s):
        List=copy.deepcopy(self.VT)
        List[-1]='#'
        s=s+'#'
        
        stack=['E','#']
        i=0
        
        date=[[0,''.join(reversed(stack)),s,'初始化']]
        num=1
        while(1):
            if s[0]==stack[0]=='#':
                break
            elif s[0]==stack[0]!='#':
                stack.pop(0)
                s=s[1:]
                row=[num,''.join(reversed(stack)),s,'','GETNEXT(I)']
                date.append(row)
            elif stack[0] in self.VN:
                X=stack.pop(0)
                ch=self.LL1_dic[X][List.index(s[0])]
                if ch!='ERR':
                    if ch!='ε':
                        temp=''.join(reversed(ch))#反序
                        for i in temp:
                            stack.insert(0,i)
                        row=[num,''.join(reversed(stack)),s,''.join([X,'->',ch]),''.join(['POP,','PUSH(',ch,')'])]
                        date.append(row)
                    else:
                        row=[num,''.join(reversed(stack)),s,''.join([X,'->',ch]),'POP']
                        date.append(row)
                else:
                     row=[num,''.join(reversed(stack)),s,'ERROR','ERROR']
                     date.append(row)
                     break
            num=num+1
        return date       

def func():
    global l,tree,entry
    input_text=entry.get()
    date=l.LL1_analyze(input_text)
    tree.delete(*tree.get_children())
    for item in date:
            tree.insert('',tk.END,values=item)                                              
        
if __name__=="__main__":
    root=tk.Tk()
    root.title("LL(1)语法分析器")
    root.geometry('900x600')
    root.geometry('+280+100')
    root.resizable(False,False)
    
    grammar_list=["E->TG",
              "G->+TG|-TG",
              "G->ε",
              "T->FS",
              "S->*FS|/FS",
              "S->ε",
              "F->(E)",
              "F->i"]
    
    l=LL1(grammar_list)
    if l.is_left_recursion():
        sys.exit()
    #辅助打表
    List=copy.deepcopy(l.VT)
    List[-1]='#'
    
    #整体布局
    Frame1=tk.Frame(root)
    Frame1.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
    Frame3=tk.Frame(root)
    Frame3.pack(fill=tk.BOTH,expand=True,side=tk.BOTTOM)
    
    Frame2=tk.Frame(Frame1)
    Frame2.pack(fill=tk.BOTH,expand=True,side=tk.RIGHT)
    #文法展示框
    grammarFrame=tk.Frame(Frame1)
    grammarFrame.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)
    grammarLabel=tk.Label(grammarFrame,text="文法",height=1,bd=1,relief=tk.SOLID)
    grammarLabel.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
    grammarText=tk.Text(grammarFrame,width=40,height=10,state='disabled')
    grammarText.pack(fill=tk.BOTH,expand=True)
    
    #展示文法
    grammarText.config(state=tk.NORMAL)
    grammarText.insert(tk.END,"\n".join(l.grammar_list))
    grammarText.config(state=tk.DISABLED)
    #输入框
    entryFrame=tk.Frame(Frame2)
    entryFrame.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
    entryLabel=tk.Label(entryFrame,text='输入',height=1)
    entryLabel.pack(fill=tk.X,expand=True,side=tk.TOP)
    entry=tk.Entry(entryFrame)
    entry.pack(fill=tk.BOTH,expand=1)
    button=tk.Button(entryFrame,text="确定",command=func)
    button.pack(fill=tk.X,expand=True,side=tk.BOTTOM)
    
    #分析表展示框
    LL1Frame=tk.Frame(Frame2)
    LL1Frame.pack(fill=tk.BOTH,expand=True,side=tk.BOTTOM)
    LL1Label=tk.Label(LL1Frame,text="分析表",height=1,bd=1,relief=tk.SOLID)
    LL1Label.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
    LL1Text=tk.Text(LL1Frame,width=75,height=10,state='disabled')
    LL1Text.pack(fill=tk.BOTH,expand=True)
    
    ##分析表展示
    LL1Text.config(state=tk.NORMAL)
    LL1Text.insert(tk.END,'\t')
    LL1Text.insert(tk.END,"\t".join(List))
    LL1Text.insert(tk.END,'\n')
    for i in l.VN:
        LL1Text.insert(tk.END,i+'\t')
        LL1Text.insert(tk.END,'\t'.join(l.LL1_dic[i]))
        LL1Text.insert(tk.END,'\n')
    LL1Text.config(state=tk.DISABLED)
    #分析栈展示框
    scrollbar=tk.Scrollbar(Frame3)
    scrollbar.pack(fill=tk.Y,side=tk.RIGHT)
    global tree
    tree=ttk.Treeview(Frame3,yscrollcommand=scrollbar.set)
    
    tree['columns']=('步骤',"分析栈",'剩余输入串',"所用产生式","动作")
    tree.column('#0',width=0,stretch=tk.NO)
    tree.column('步骤',width=20)
    tree.column("分析栈",width=50)
    tree.column("剩余输入串",width=50)
    tree.column("所用产生式",width=50)
    tree.column("动作",width=50)
    
    tree.heading('步骤',text='步骤')
    tree.heading("分析栈",text="分析栈")
    tree.heading("剩余输入串",text="剩余输入串")
    tree.heading("所用产生式",text="所用产生式")
    tree.heading("动作",text="动作")   
            
    scrollbar.config(command=tree.yview)
    tree.pack(fill=tk.BOTH,expand=True)
    
    tk.mainloop()
    try:
        root.destroy()
    except tk.TclError as e:
        print("窗口已经销毁")
