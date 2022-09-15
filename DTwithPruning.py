import os
import math
import random
from matplotlib import pyplot as plt

class DataTable:
	
	def __init__(self):
		
		self.Data = [];
		self.Attribs = [];
		self.AttribsName = {};
		self.AttribsNameList = [];
	
	def InsertRow(self , DataRow):
		
		DividedRow = DataRow.split(',');
		self.Data.append([]);
		
		if len(self.Data) == 1:
			for i in range(len(DividedRow)):
				self.Attribs.append({DividedRow[i]:0 , 0:DividedRow[i]});
				self.Data[0].append(0);
			return;
		
		for i in range(len(DividedRow)):
			try:
				self.Data[-1].append(self.Attribs[i][DividedRow[i]]);
			except:
				self.Data[-1].append(len(self.Attribs[i])>>1);
				self.Attribs[i].update({DividedRow[i]:(len(self.Attribs[i])>>1) , (len(self.Attribs[i])>>1):DividedRow[i]});
		return;
	
	def InsertFromFile(self , FileAddress, Percent = 100):
		
		fp = open(FileAddress , 'r');
		k = 0;
		N = self.file_len(FileAddress);
		for i , line in enumerate(fp):
			line = line.replace("\n","");
			line = line.replace(" ","");
			self.InsertRow(line);
			if i == N*Percent/100.0:
				break;
		return;
	
	def append(self , Table):
		for i in range(len(Table.Data)):
			self.InsertRow(Table.GetLine(i));
		return;
	
	def file_len(self , fname):
		with open(fname) as f:
			for i, l in enumerate(f):
				pass
		return i + 1
	
	def InsertAttribsName(self , Names):
		self.AttribsNameList = Names;
		for i in range(len(Names)):
			self.AttribsName.update({Names[i]:i});
		return;
			
	def SortByAttrib(self , Name):
		
		self.Data = sorted(self.Data , key=lambda l:l[self.AttribsName[Name]]);
		return;
		
	def GetLine(self , i):
		tmp = self.Data[i];
		result = '';
		for j in range(len(tmp)-1):
			result += self.Attribs[j][tmp[j]] + ',';
		result += self.Attribs[j+1][tmp[j+1]];
		return result;
	
	def GetDict(self , i):
		tmp = self.Data[i];
		result = {};
		for j in range(len(tmp)):
			result.update({self.AttribsNameList[j] : self.Attribs[j][tmp[j]]});
		return result;
	
	def GetColumn(self , Name):
		result = [];
		for row in self.Data:
			result.append(row[self.AttribsName[Name]]);
		return result;
	
	def Split(self , percent):
		data1 = DataTable();
		data2 = DataTable();
		
		N = len(self.Data);
		
		for i in range(int(percent * N / 100)):
			data1.InsertRow(self.GetLine(i));
		
		for i in range(int(percent * N / 100) , N):
			data2.InsertRow(self.GetLine(i));
		
		data1.InsertAttribsName(self.AttribsNameList);
		data2.InsertAttribsName(self.AttribsNameList);
		return [data1 , data2];
	
	def RandomSplit(self , percent):
		data1 = DataTable();
		data2 = DataTable();
		
		N = len(self.Data);
		x = random.sample(range(N) , int(percent * N / 100));
		for i in range(N):
			if i in x:
				data1.InsertRow(self.GetLine(i));
			else:
				data2.InsertRow(self.GetLine(i));
		
		data1.InsertAttribsName(self.AttribsNameList);
		data2.InsertAttribsName(self.AttribsNameList);
		return [data1 , data2];
	
	def Print(self):
		for line in self.Data:
			print(line)
		return
		
class DecisionTree:
			
	def __init__(self , dataTable , baseAttrib , percent , dopruning = True , validTable = 0 , pruningThreshhold = 0 , deep = -1):
		self.baseAttrib = baseAttrib;
		if validTable == 0:
			splitTable = dataTable.RandomSplit(percent);
		else:
			tmpTable = dataTable.RandomSplit(percent);
			splitTable = [tmpTable[0] , validTable];
		if deep == -1:
			deep = len(dataTable.AttribsNameList) - 1;
		self.root = self.makeTree(splitTable[0] , baseAttrib , deep);
		if dopruning:
			self.root = self.pruning(self.root , splitTable[1] , baseAttrib, pruningThreshhold);
		self.Nodes = self.NodeNumber(self.root) + 1;
	
	def NodeNumber(self , node):
		result = 0;
		for x , y in node.child.items():
			result += self.NodeNumber(y);
		result += len(node.child);
		return result;
		
	class DecisionTreeNode:
		
		def __init__(self , Label , Value , MeanValue = 0):
			self.Label = Label;
			self.Value = Value;
			self.child = {};
			if not (MeanValue == 0):
				self.MeanValue = MeanValue;
			else:
				self.MeanValue = Value;
			
		def AddChild(self , desicionTreeNode , Attrib):
			self.child.update({Attrib:desicionTreeNode});
			
		def copy(self):
			newNode = DecisionTree.DecisionTreeNode(self.Label , self.Value , self.MeanValue);
			for attrib , node in self.child.items():
				newNode.AddChild(node.copy() , attrib);
			return newNode;
	
	def Entropy(self , dataTable , Attrib):
		
		result = 0;
		NA = len(dataTable.Attribs[dataTable.AttribsName[Attrib]])>>1;
		p = [0 for i in range(NA)];
		N = len(dataTable.Data);
		
		for i in range(N):
			p[dataTable.Data[i][dataTable.AttribsName[Attrib]]] += 1;
		
		for i in range(NA):
			result += -p[i]*math.log((p[i]/float(N)) , 2)/N;
		return result;
		
	def AverageInformationEntropy(self , dataTable , baseAttrib , Attrib):
	
		result = 0;
		N = len(dataTable.Data);
	
		dataTable.SortByAttrib(Attrib);
		tmp = DataTable();
		tmp.InsertAttribsName(dataTable.AttribsNameList);
		tmp.InsertRow(dataTable.GetLine(0));
	
		for i in range(1,N):
			if (dataTable.Data[i][dataTable.AttribsName[Attrib]] == dataTable.Data[i-1][dataTable.AttribsName[Attrib]]):
				tmp.InsertRow(dataTable.GetLine(i));
			else:
				result += self.Entropy(tmp , baseAttrib) * len(tmp.Data) / float(N);
				tmp = DataTable();
				tmp.InsertAttribsName(dataTable.AttribsNameList);
				tmp.InsertRow(dataTable.GetLine(i));
	
		result += self.Entropy(tmp , baseAttrib) * len(tmp.Data) / float(N);
		return result;
	
	def InformationGain(self , dataTable , baseAttrib , Attrib):
		return self.Entropy(dataTable , baseAttrib) - self.AverageInformationEntropy(dataTable , baseAttrib , Attrib);
	
	def makeTree(self , dataTable , baseAttrib , n):
		
		tmplist = dataTable.GetColumn(baseAttrib);
		if len(set()) == 1 or n == 0:
			return self.DecisionTreeNode(baseAttrib , dataTable.Attribs[dataTable.AttribsName[baseAttrib]][int(round(sum(tmplist)/float(len(tmplist))))]);
		
		maxgain = -1;
		maxgainattrib = "";
		for name in dataTable.AttribsNameList:
			if name == baseAttrib:
				continue;
			else:
				tmpgain = self.InformationGain(dataTable , baseAttrib , name);
				if maxgain < tmpgain:
					maxgain = tmpgain;
					maxgainattrib = name;
		
		if maxgain == 0:
			return self.DecisionTreeNode(baseAttrib , dataTable.Attribs[dataTable.AttribsName[baseAttrib]][int(round(sum(tmplist)/float(len(tmplist))))]);
		
		thisnode = self.DecisionTreeNode(maxgainattrib , "" , dataTable.Attribs[dataTable.AttribsName[baseAttrib]][int(round(sum(tmplist)/float(len(tmplist))))]);
		dataTable.SortByAttrib(maxgainattrib);
		N = len(dataTable.Data);
		tmptable = DataTable();
		tmptable.InsertAttribsName(dataTable.AttribsNameList);
		tmptable.InsertRow(dataTable.GetLine(0));
		k = [dataTable.Data[0][dataTable.AttribsName[maxgainattrib]]];
		for i in range(1,N):
			if (dataTable.Data[i][dataTable.AttribsName[maxgainattrib]] == dataTable.Data[i-1][dataTable.AttribsName[maxgainattrib]]):
				tmptable.InsertRow(dataTable.GetLine(i));
			else:
				childnode = self.makeTree( tmptable , baseAttrib , n-1);
				thisnode.child.update({dataTable.Attribs[dataTable.AttribsName[maxgainattrib]][k[-1]]:childnode});
				k.append(dataTable.Data[i][dataTable.AttribsName[maxgainattrib]]);
				tmptable = DataTable();
				tmptable.InsertAttribsName(dataTable.AttribsNameList);
				tmptable.InsertRow(dataTable.GetLine(i));
				
		childnode = self.makeTree( tmptable , baseAttrib , n-1);
		thisnode.child.update({dataTable.Attribs[dataTable.AttribsName[maxgainattrib]][k[-1]]:childnode});

		return thisnode;
	
	def result(self , AttribDictionary , thisnode = 0):
		
		if thisnode == 0:
			thisnode = self.root;
		
		while True:
			if not(thisnode.Value == ""):
				return thisnode.Value;
			try:	
				thisnode = thisnode.child[AttribDictionary[thisnode.Label]];
			except:
				return 0;
	
	def pruning(self , node , dataTable , baseAttrib, pruningThreshhold):
		
		if node.Label == baseAttrib:
			#print "Leaf"
			return node;
		if len(dataTable.Data) == 0:
			#print "No Data"
			return node;
		
		dataTable.SortByAttrib(node.Label);
		tmptable = DataTable();
		tmptable.InsertAttribsName(dataTable.AttribsNameList);
		tmptable.InsertRow(dataTable.GetLine(0));
		N = len(dataTable.Data);
		
		newnode = self.DecisionTreeNode(baseAttrib , node.MeanValue , node.MeanValue);
		for i in range(1,N):
			if (dataTable.Data[i][dataTable.AttribsName[node.Label]] == dataTable.Data[i-1][dataTable.AttribsName[node.Label]]):
				tmptable.InsertRow(dataTable.GetLine(i));
			else:
				try:
					tmpattrib = dataTable.Attribs[dataTable.AttribsName[node.Label]][dataTable.Data[i-1][dataTable.AttribsName[node.Label]]];
					tmpnode = node.child[tmpattrib].copy();
					node.child.update({tmpattrib : self.pruning(tmpnode , tmptable , baseAttrib, pruningThreshhold)});
				except:
					pass
				tmptable = DataTable();
				tmptable.InsertAttribsName(dataTable.AttribsNameList);
				tmptable.InsertRow(dataTable.GetLine(i));
		try:
			tmpattrib = dataTable.Attribs[dataTable.Data[i-1][dataTable.AttribsName[node.Label]]];
			tmpnode = node.child[tmpattrib].copy();
			node.child.update({tmpattrib : self.pruning(tmpnode , tmptable , baseAttrib , pruningThreshhold)});
		except:
			pass
		#check accuracy
		oldnodeaccuracy = 0;
		newnodeaccuracy = 0;
		
		for i in range(N):
			tmpdict = dataTable.GetDict(i);
			oldnoderes = self.result(tmpdict , node);
			newnoderes = self.result(tmpdict , newnode);
			oldnodeaccuracy += int(oldnoderes == tmpdict[baseAttrib]);
			newnodeaccuracy += int(newnoderes == tmpdict[baseAttrib]);
		
		if newnodeaccuracy >= oldnodeaccuracy*(1 + pruningThreshhold/100.0):
			#print "prun"
			return newnode;
		
		#print "not prun"
		return node;
	
	def Print(self , node = 0 , pretype = "" , attrib = ""):
		if node == 0:
			node = self.root;
		string = pretype + attrib + "--> ";
		if node.Label == self.baseAttrib:
			string += node.Value;
			#print(string);
			return string + "\n";
			
		string += node.Label;
		string += ":";
		for i in range(len(node.Label + attrib)+4):
			pretype += " ";
		#print(string);
		string += "\n"
		k = 0;
		for x , y in node.child.items():
			k += 1;
			if k == len(node.child):
				for i in range(2):
					string += pretype + "|\n";
				string += self.Print(node = y , pretype = pretype + " " , attrib = x);
			else:
				for i in range(2):
					string += pretype + "|\n";
				string += self.Print(node = y , pretype = pretype + "|" , attrib = x);
		
		return string;
	
def TreeAccuracy(tree , testtable):
	trueanswer = 0;
	allanswer = 0;
	for i in range(len(testtable.Data)):
		line = testtable.GetLine(i);
		attribs = line.split(",");
		attribdict = {};
		for i in range(1,len(attribs)):
			attribdict.update({attriblist[i]:attribs[i]});
		res = tree.result(attribdict);
		if attribs[0] == res:
			trueanswer += 1;
		allanswer += 1;
	return round(trueanswer*10000 / float(allanswer))/100.00;
		
if __name__ == '__main__':	

	script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

	attriblist = ['salary',
				  'workclass',
				  'education',
				  'marital-status',
				  'occupation',
				  'relationship',
				  'race',
				  'sex',
				  'native-country'];
				 
	dtable = DataTable();
	dtable.InsertFromFile(os.path.join(script_dir , 'Data Set/adult.train.10k.discrete'))
	dtable.InsertAttribsName(attriblist);
	ttable = DataTable();
	ttable.InsertFromFile(os.path.join(script_dir , 'Data Set/adult.test.10k.discrete'))
	ttable.InsertAttribsName(attriblist);
	dtable1 = dtable;
	ttable = ttable.RandomSplit(50);
	
	tree = [];
	x = [];
	y = [];
	string = "*"
	for i in range(6):
		string += string;
	try:
		mytreefile = open(os.path.join(script_dir , "Tree.txt") , "x");
	except:
		mytreefile = open(os.path.join(script_dir , "Tree.txt") , "w");
	for i in range(len(attriblist)):
		tree.append(DecisionTree(dataTable = dtable , baseAttrib = 'salary' , percent = 100 , dopruning = True , validTable = ttable[0] , pruningThreshhold = 0.5 , deep = i));
		x.append(tree[-1].Nodes);
		y.append([TreeAccuracy(tree[-1] , dtable) , TreeAccuracy(tree[-1] ,ttable[0]) , TreeAccuracy(tree[-1] , ttable[1])]);
		#print(tree[-1].Print());
		#print(string);
		mytreefile.write(tree[-1].Print() + "\n" + string + "\n");
	plt.plot(x , y);
	plt.legend(("On train" , "On Valid" , "On Test"));
	plt.grid();
	plt.title("100% Data Table as Data , 50% Test Data as Valid , 50% Test Data as Test"); 
	plt.show();
	'''
	attribdict = {'workclass':'Private',
				  'education':'11th',
				  'marital-status':'Never-married',
				  'occupation':'Machon-op-inspct',
				  'relationship':'Own-child',
				  'race':'black',
				  'sex':'male',
				  'native-country':'United-States'}
	print(tree.result(attribdict));
	
	#test tree
	tree = DecisionTree(dataTable = dtable[0] , baseAttrib = 'salary' , percent = 100 , dopruning = True , validTable = dtable[1] , pruningThreshhold = 0.5);
	print(tree.Nodes);
	print(TreeAccuracy(tree , dtable1));
	print(TreeAccuracy(tree , ttable));
	
	trueanswer = 0;
	allanswer = 0;
	for i in range(len(ttable.Data)):
		line = ttable.GetLine(i);
		attribs = line.split(",");
		attribdict = {};
		for i in range(1,len(attribs)):
			attribdict.update({attriblist[i]:attribs[i]});
		res = tree[-1].result(attribdict);
		if attribs[0] == res:
			trueanswer += 1;
		allanswer += 1;
		#if res == 0:
		#	print(attribs);
	print("accuracy:");
	print(round(trueanswer*10000 / float(allanswer))/100.00);
	
	#tree.Print();
	'''
