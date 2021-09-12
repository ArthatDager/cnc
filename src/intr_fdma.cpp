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
int* share_int( key_t key)
{
static int *b;
int shmid;
	if ((shmid = shmget(key, 1, IPC_CREAT | 0666)) < 0) {
		std::cerr<<"shmget"<<(shmid = shmget(key, 1, IPC_CREAT | 0666));
		exit(1);
	}
	/*
	 * Now we attach the segment to our data space.
	 */
	if ((b = (int *)shmat(shmid, 0, 0)) == (int *) -1) {
		std::cerr<<"shmat";
		exit(1);
	}
return b;
};


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
	//int shmid;
	key_t key;
	static int *b;

	key = 5677;

	/*
	 * Create the eight bit  segment.
	 */
/*
	if ((shmid = shmget(key, 1, IPC_CREAT | 0666)) < 0) 
	{
		cerr<<"shmget";
		exit(1);
	}
*/
	/*
	 * Now we attach the segment to our data space.
	 */
/*	if ((b = ( int *)shmat(shmid, 0, 0)) == (int *) -1) 
	{
		cerr<<"shmat";
		exit(1);

	}
*/
	b = share_int(key);	
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
	int b_int, b_old=0, b_loc ;
        string m_send;
	char msg_sock[10];
	bool toggle_pause=false;
        *b=0;
	while(1)
	{
		bzero(buffer,8);
		n = read(newsockfd,buffer,8);
		b_int=atoi(buffer);
		//printf("b_int = %d\n",b_int);
		if(b_int!=16)
		{
			if(b_int==1) //line_status
			{
				b_loc=(*b);
				if(b_loc>=0)
					m_send=patch::to_string(b_loc);
				else
				{
				if(b_loc==(-20))
					m_send="-1";
				}
				strncpy( msg_sock,m_send.c_str(), sizeof(msg_sock));
				//printf("line Status is : %s",msg_sock);	
				n=write(newsockfd,msg_sock,8);
			}
			if(b_int==2)
			{
				printf("design get pause");
				if(toggle_pause)
				{
					toggle_pause=false;
					*b=1;
					n=write(newsockfd,"RESUME",8);
				}	
				else
				{
					toggle_pause=true;
                                	*b=-1;
					n=write(newsockfd,"PAUSE",8);
				} 
			}
		}
		else
		{
		*b=-5;     
		n=write(newsockfd,"STOP",8);
		}
		//istr=patch::to_string(i);
		//strncpy( ival,istr.c_str(), sizeof(ival));
		//n = write(newsockfd,ival,3);
		//n = write(newsockfd,"ok",2);
		if (n < 0) error("Error: wrong Capture");
		if (b_int==16)break;
	}     
	close(newsockfd);
	close(sockfd);
	return 0; 
}

