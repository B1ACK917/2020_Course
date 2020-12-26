#include <iostream>
#include <mysql.h>
#include <string>
using namespace std;

#define DO_QUERY(a,b) if(mysql_query(a,b)) throw string(mysql_error(a))

//显示sc表
void show_sc_table(MYSQL & mysql) {
	DO_QUERY(&mysql, "select * from sc");
	//获取查询结果
	MYSQL_RES* result = mysql_store_result(&mysql);
	//获取总行数
	uint64_t row_num = mysql_num_rows(result);
	//获取总列数
	int num_fields = mysql_num_fields(result);
	//获取每一列名称
	MYSQL_FIELD* fields = mysql_fetch_fields(result);
	//显示表头
	for (auto i = 0; i < num_fields; i++)
		cout << fields[i].name << "\t";
	cout << endl;
	//依次输出每一行
	for (auto i = 0;i < row_num;++i) {
		MYSQL_ROW row = mysql_fetch_row(result);
		for (auto j = 0;j < num_fields;++j)
			cout << row[j] << "\t";
		cout << endl;
	}
}

void insert_rows_into_sc_table(MYSQL& mysql) {
	string query_head = "insert into sc value";
	string new_query = "";
	string sno, cno, grade;
	char c;
	cout << "Ready To Insert Value Into SC Table" << endl;
	while (1) {
		//读入参数
		new_query = query_head;
		cout << "Please input sno (eg:10086): ";
		cin >> sno;
		cout << "Please input cno (eg:001): ";
		cin >> cno;
		cout << "Please input grade (eg:78): ";
		cin >> grade;
		//构造语句
		new_query += "('" + sno + "','" + cno + "'," + grade + ");";
		//执行插入
		DO_QUERY(&mysql, new_query.c_str());
		//显示sc表
		show_sc_table(mysql);
		cout << "Insert again? y:yes,n:no\t";
		cin >> c;
		if (c == 'n')
			break;
	}
}

int main() {
	//一些常量定义，数据库账户密码等
	int num = 0;
	char host[] = "localhost";
	char account[] = "root";
	char key[] = "B1ack@917";
	char database[] = "jxgl";
	int port = 3306;
	MYSQL mysql;
	try {
		//使用mysql_init初始化MYSQL结构
		if (!mysql_init(&mysql))
			throw string("Initialize MYSQL Failed");
		//使用account,key连接到数据库
		if (!mysql_real_connect(&mysql, host, account, key, database, port, 0, 0))
			throw string("Connect To " + string(database) + " Failed");
		cout << "Connect to " << database << " Succeed" << endl;
		//设置GBK编码以显示汉字
		DO_QUERY(&mysql, "SET NAMES gbk;");
		if (mysql_list_tables(&mysql, "sc")->row_count) {
			//检测是否已经存在sc表
			cout << "SC Table Already Exists, Dropping" << endl;
			//如果存在，删除sc表
			DO_QUERY(&mysql, "drop table sc;");
			cout << "Dropped SC Table" << endl;
		}
		//创建sc表
		DO_QUERY(&mysql, "create table sc(sno char(16), cno char(16), grade int);");
		cout << "Create SC Table" << endl;
		insert_rows_into_sc_table(mysql);
	}
	catch (string& errorMessage) {
		cout << errorMessage << endl;
	}
	return 0;
}