#include<iostream>
#include<cstdlib>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <sstream>

#define SHMSZ    1024
using namespace std;

void error(const char *msg)
{
	perror(msg);
	exit(1);
}
namespace patch
{
	template < typename T > std::string to_string( const T& n )
	{
		std::ostringstream stm ;
		stm << n ;
		return stm.str() ;
	}
}
int main(int argc, char *argv[])
{
	int sockfd, newsockfd, portno;
	socklen_t clilen;
	char buffer[256],ival[3]=" ";
	std::string istr;
	struct sockaddr_in serv_addr, cli_addr;
	int n,i=0;
	std::ostringstream convert;
	if (argc < 2) {
		fprintf(stderr,"ERROR, no port provided\n");
		exit(1);
	}

	char c;
	int shmid;
	key_t key;
	static int *b;

	key = 5679;

	/*
	 * Create the eight bit  segment.
	 */
	if ((shmid = shmget(key, 1, IPC_CREAT | 0666)) < 0) 
	{
		cerr<<"shmget";
		exit(1);
	}

	/*
	 * Now we attach the segment to our data space.
	 */
	if ((b = ( int *)shmat(shmid, 0, 0)) == (int *) -1) 
	{
		cerr<<"shmat";
		exit(1);

	}

	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) 
		error("ERROR opening socket");
	bzero((char *) &serv_addr, sizeof(serv_addr));
	portno = atoi(argv[1]);
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(portno);
	if (bind(sockfd, (struct sockaddr *) &serv_addr,
				sizeof(serv_addr)) < 0) 
		error("ERROR on binding");
	listen(sockfd,5);
	clilen = sizeof(cli_addr);
	newsockfd = accept(sockfd, 
			(struct sockaddr *) &cli_addr, 
			&clilen);
	if (newsockfd < 0) 
		error("ERROR on accept");
	bzero(buffer,256);
	n = read(newsockfd,buffer,255);
	if (n < 0) error("ERROR reading from socket");
	printf("SERVER: %s\n",buffer);
	bzero(buffer,256);
	int b_int, b_old=0;
	while(1)
	{
		bzero(buffer,4);
		n = read(newsockfd,buffer,4);
		b_int=atoi(buffer);
		printf("b_int = %d\n",b_int);
		if(b_int!=16)
		{
			if(b_int==1)
			{
				b_int=(b_old&12)|1;
			}
			if(b_int==2)
			{
				b_int=(b_old&12)|3;
			}
			if(b_int==4)
			{
				b_int=(b_old&3)|4;
			}
			if(b_int==8)
			{
				b_int=(b_old&3)|12;
			}
		}
		*b=b_int;     
		//istr=patch::to_string(i);
		//strncpy( ival,istr.c_str(), sizeof(ival));
		//n = write(newsockfd,ival,3);
		printf("SERVER: %s\n",buffer);
		n = write(newsockfd,"ok",2);
		if (n < 0) error("Error: wrong Capture");
		if (b_int==16)break;
		b_old=b_int; 
	}     
	close(newsockfd);
	close(sockfd);
	return 0; 
}

