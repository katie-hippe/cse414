# a 

CREATE TABLE sales (
	name varchar(20),
	discount varchar(10),
	month varchar(10),
	price int
);

# .mode tabs
# .import C:\Users\katie\OneDrive\Documents\Schoolwork\4.2\cse_414\hw4\mrFrumbleData.txt sales --skip 1



# b

# find out function dependencies: 

# found these ones:

# n->p
SELECT * 
FROM sales s1, sales s2
WHERE s1.name = s2.name AND s1.price <> s2.price;

# m->d
SELECT *
FROM sales s1, sales s2
WHERE s1.month = s2.month AND s1.discount <> s2.discount;

# example of one that doesn't: d->p
SELECT * 
FROM sales s1, sales s2
WHERE s1.discount = s2.discount AND s1.price <> s2.discount;



# c

# S(n,p,d,m)
# 	S1: (n,p)
#	S2: (n,d,m)
#		S3: (d,m)
#		S4: (n,m)

# BCNF: S1: (n,p)
#	S2: (n,m)
#	S3: (d,m)

CREATE TABLE np 
	(name varchar(20) PRIMARY KEY,
	price int);

CREATE TABLE dm
	(month varchar(20) PRIMARY KEY,
	discount varchar(10));

CREATE TABLE nm 
	(name varchar(20),
	month varchar(10),
	FOREIGN KEY (name) REFERENCES np(name),
	FOREIGN KEY (month) REFERENCES dm(month));



# d.

INSERT INTO np
SELECT DISTINCT name, price FROM sales;

SELECT COUNT(*) FROM np;
# 36 rows

INSERT INTO dm
SELECT DISTINCT month,discount FROM sales;

SELECT COUNT(*) FROM dm;
# 12 rows 

INSERT INTO nm 
SELECT DISTINCT name, month FROM sales;

SELECT COUNT(*) FROM nm;
# 426 rows 
