#include <stdio.h>
#include <pigpio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <unistd.h>
#include <cstdlib>
#include <iostream>

#define WAVES 1
#define XS 25
#define XD 24
#define YS 23 
#define YD 18 
#define TS 7
 
int* share_int(key_t key)
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


int main(int argc, char *argv[])
{
	FILE *stp, *tim;
	int wid;
	char wstp[1];
	int i,j,k,m;
	int turn=21;
	int stepping,xstep,ystep,tstep;
	int timing,timing_n;
	int d_line_count=0;
	float scale=1;
	float t=0;
	if(argc>1)
		scale=((float)(atoi(argv[1])));

	stp = fopen("./motion/step1.txt", "r");
	tim = fopen("./motion/time1.txt", "r");

	const int steps= 100;
	gpioPulse_t pluseX[steps];
	gpioPulse_t pluseY[steps];
	gpioPulse_t dirX[steps];
	gpioPulse_t dirY[steps];
	gpioPulse_t tsw[steps];

	char c;
	static int *b;
	int pos=0; 
	key_t key;
	key = 5677;
#if 0	
	int shmid;

	/*
	 * Create the eight bit  segment.
	 */

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
#else
	b=share_int(key);
#endif
	if (gpioInitialise()<0) return -1;
	gpioSetMode(XS, PI_OUTPUT);
	gpioSetMode(YS, PI_OUTPUT);
	gpioSetMode(XD, PI_OUTPUT);
	gpioSetMode(YD, PI_OUTPUT);
	gpioSetMode(TS, PI_OUTPUT);
	gpioWaveClear();
	char buff[12];
	char buffc[12];
        i=0;
        j=0;
        k=0;
	bool first = 0;
        timing = 10;
        tstep=0;
        int b_local=0,b_old=0;
	*b=0;
	while(!feof(stp))
	{
		if(*b==(-1))
		{
			b_old=-1;
			continue;
		}
		if(*b==(-5))
			exit(1);
		fgets(buffc,9,stp);
		d_line_count++; 
                if(d_line_count>16)
		{
		if(b_old != (-1))
		{
			b_old=0;	
			b_local=(*b);
		}
		b_local+=d_line_count;
		d_line_count=0;
		*b=b_local;
		} 
		stepping = atoi(buffc);
		fgets(buff,9,tim); 
		timing_n = ((atoi(buff)*scale)/1000);
                timing= (timing_n<=0)?1:timing_n;
                if((stepping==0)|stepping==9)
		{	
		    tstep = (stepping==0)?1:0;
                    continue;
		}
               // if(tstep)
                //    printf("%d,%d",stepping,timing);
		//getchar(); 
		xstep = (stepping!=7)&(stepping!=3)&(stepping!=0)&(stepping!=9)?1:0;
		xstep = (stepping==2)|(stepping==1)|(stepping==8)?xstep:-xstep;
		
		ystep = (stepping!=1)&(stepping!=5)&(stepping!=0)&(stepping!=9)?1:0;
		ystep = (stepping==2)|(stepping==3)|(stepping==4)?ystep:-ystep;

		switch (xstep)
		{
		
		case -1:
			pluseX[i].gpioOn=1<<XS;
			pluseX[i].gpioOff=0;
			pluseX[i].usDelay=timing;

			dirX[i].gpioOn=1<<XD;
			dirX[i].gpioOff=0;
			dirX[i].usDelay=timing;
			i++;

			pluseX[i].gpioOn=0;
			pluseX[i].gpioOff=1<<XS;
			pluseX[i].usDelay=timing;

			dirX[i].gpioOn=1<<XD;
			dirX[i].gpioOff=0;
			dirX[i].usDelay=timing;
			i++;
			break;
		case 1:
		
			pluseX[i].gpioOn=1<<XS;
			pluseX[i].gpioOff=0;
			pluseX[i].usDelay=timing;

			dirX[i].gpioOn=0;
			dirX[i].gpioOff=1<<XD;
			dirX[i].usDelay=timing;
			i++;

			pluseX[i].gpioOn=0;
			pluseX[i].gpioOff=1<<XS;
			pluseX[i].usDelay=timing;

			dirX[i].gpioOn=0;
			dirX[i].gpioOff=1<<XD;
			dirX[i].usDelay=timing;
			i++;
		break;
		case 0:
		
			pluseX[i].gpioOn=0;
			pluseX[i].gpioOff=1<<XS;
			pluseX[i].usDelay=timing;

			dirX[i].gpioOn=0;
			dirX[i].gpioOff=1<<XD;
			dirX[i].usDelay=timing;
			i++;

			pluseX[i].gpioOn=0;
			pluseX[i].gpioOff=1<<XS;
			pluseX[i].usDelay=timing;

			dirX[i].gpioOn=0;
			dirX[i].gpioOff=1<<XD;
			dirX[i].usDelay=timing;
			i++;
		break;

		}
		switch (ystep)
		{
		
		case -1:
			pluseY[j].gpioOn=1<<YS;
			pluseY[j].gpioOff=0;
			pluseY[j].usDelay=timing;

			dirY[j].gpioOn=1<<YD;
			dirY[j].gpioOff=0;
			dirY[j].usDelay=timing;
			j++;

			pluseY[j].gpioOn=0;
			pluseY[j].gpioOff=1<<YS;
			pluseY[j].usDelay=timing;

			dirY[j].gpioOn=1<<YD;
			dirY[j].gpioOff=0;
			dirY[j].usDelay=timing;
			j++;
			break;
		case 1:
		
			pluseY[j].gpioOn=1<<YS;
			pluseY[j].gpioOff=0;
			pluseY[j].usDelay=timing;

			dirY[j].gpioOn=0;
			dirY[j].gpioOff=1<<YD;
			dirY[j].usDelay=timing;
			j++;

			pluseY[j].gpioOn=0;
			pluseY[j].gpioOff=1<<YS;
			pluseY[j].usDelay=timing;

			dirY[j].gpioOn=0;
			dirY[j].gpioOff=1<<YD;
			dirY[j].usDelay=timing;
			j++;
		break;
		case 0:
		
			pluseY[j].gpioOn=0;
			pluseY[j].gpioOff=1<<YS;
			pluseY[j].usDelay=timing;

			dirY[j].gpioOn=0;
			dirY[j].gpioOff=1<<YD;
			dirY[j].usDelay=timing;
			j++;

			pluseY[j].gpioOn=0;
			pluseY[j].gpioOff=1<<YS;
			pluseY[j].usDelay=timing;

			dirY[j].gpioOn=0;
			dirY[j].gpioOff=1<<YD;
			dirY[j].usDelay=timing;
			j++;
		break;

		}

        	switch (tstep)
        	{
        	case 1:
        		tsw[k].gpioOn=0;
        		tsw[k].gpioOff=1<<TS;
        		tsw[k].usDelay=timing;
        		k++;
         		tsw[k].gpioOn=0;
        		tsw[k].gpioOff=1<<TS;
        		tsw[k].usDelay=timing;
        		k++;

        	break;
        	case 0:
         		tsw[k].gpioOn=1<<TS;
        		tsw[k].gpioOff=0;
        		tsw[k].usDelay=timing;
        		k++;
        		tsw[k].gpioOn=1<<TS;
        		tsw[k].gpioOff=0;
        		tsw[k].usDelay=timing;
        		k++;
        	break;
        	}
		
		if(i==steps)
		{  	
			gpioWaveAddGeneric(i, pluseX); 
			gpioWaveAddGeneric(i, pluseY); 
			gpioWaveAddGeneric(i, dirX);
			gpioWaveAddGeneric(i, dirY);
		        gpioWaveAddGeneric(k, tsw);
			wid = gpioWaveCreate();
			wstp[0]=wid;
			while (gpioWaveTxBusy());
			gpioWaveChain(wstp,1);
			
			while (gpioWaveTxBusy());
			gpioWaveClear();
			i=0;	
                        j=0;
                        k=0;
		}
	}
	gpioWaveClear();
	gpioWaveAddGeneric(i-1, pluseX); 
	gpioWaveAddGeneric(j-1, pluseY); 
	gpioWaveAddGeneric(i-1, dirX);
	gpioWaveAddGeneric(j-1, dirY);
	gpioWaveAddGeneric(k-1, tsw);
	while (gpioWaveTxBusy());
	wid = gpioWaveCreate();
	gpioWaveChain(wstp,1);
	while (gpioWaveTxBusy());
	*b=-20;
	gpioTerminate();
}

