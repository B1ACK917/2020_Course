#include <iostream>
#include <mysql.h>
#include <string>
using namespace std;

#define DO_QUERY(a,b) if(mysql_query(a,b)) throw string(mysql_error(a))

int main() {
	//一些常量定义，数据库账户密码等
	int num = 0;
	char fu[2];
	char host[] = "localhost";
	char account[] = "root";
	char key[] = "B1ack@917";
	char database[] = "jxgl";
	int port = 3306;
	MYSQL mysql;
	try {
		//使用mysql_init初始化MYSQL结构
		if(!mysql_init(&mysql))
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
	}
	catch (string& errorMessage) {
		cout << errorMessage << endl;
	}
	return 0;
}