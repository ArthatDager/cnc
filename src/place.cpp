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

int main(int argc, char *argv[])
{
	int wid;
	char wstp[1];
	int i,j,k,m;
	int turn=21;
	int stepping,xstep,ystep,tstep;
	int timing,timing_n;
	float scale=1;
	float t=0;
	if(argc>1)
		scale=((float)(atoi(argv[1])));

	const int steps= 20;
	gpioPulse_t pluseX[2*steps];
	gpioPulse_t pluseY[2*steps];
	gpioPulse_t dirX[2*steps];
	gpioPulse_t dirY[2*steps];

	char c;
	int shmid;
	key_t key;
	static int *b;
	int pos=0; 
	key = 5679;

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

	if (gpioInitialise()<0) return -1;
	gpioSetMode(XS, PI_OUTPUT);
	gpioSetMode(YS, PI_OUTPUT);
	gpioSetMode(XD, PI_OUTPUT);
	gpioSetMode(YD, PI_OUTPUT);
	gpioWaveClear();
	char buff[12];
	char buffc[12];
        int bh2, bl2; 
	i=0;
	j=0;
	k=0;
	bool first = 0;
	timing = 1000;
	tstep=0;
	*b=0;
	while(1)
	{
         bh2=((*b>>2)&3); 
         bl2=((*b)&3);
          
		if(bl2==1)
		{
			for(i=0;i<steps;i++)
			{
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
			}
		}
		else if(bl2==3)
		{
			for(i=0;i<steps;i++)
			{
				pluseX[i].gpioOn=1<<XS;
				pluseX[i].gpioOff=0;
				pluseX[i].usDelay=timing;

				dirX[i].gpioOff=1<<XD;
				dirX[i].gpioOn=0;
				dirX[i].usDelay=timing;
				i++;
				pluseX[i].gpioOn=0;
				pluseX[i].gpioOff=1<<XS;
				pluseX[i].usDelay=timing;

				dirX[i].gpioOff=1<<XD;
				dirX[i].gpioOn=0;
				dirX[i].usDelay=timing;
			}
		}
		else if(bl2 == 0)
		{
			for(i=0;i<steps;i++)
			{
				pluseX[i].gpioOn=1<<XS;
				pluseX[i].gpioOff=0;
				pluseX[i].usDelay=timing;

				dirX[i].gpioOff=1<<XD;
				dirX[i].gpioOn=0;
				dirX[i].usDelay=timing;
				i++;
				pluseX[i].gpioOff=0;
				pluseX[i].gpioOn=1<<XS;
				pluseX[i].usDelay=timing;

				dirX[i].gpioOff=1<<XD;
				dirX[i].gpioOn=0;
				dirX[i].usDelay=timing;
			}


		}
		if(bh2==1)
		{
			for(i=0;i<steps;i++)
			{
				pluseY[i].gpioOn=1<<YS;
				pluseY[i].gpioOff=0;
				pluseY[i].usDelay=timing;

				dirY[i].gpioOn=1<<YD;
				dirY[i].gpioOff=0;
				dirY[i].usDelay=timing;
				i++;
				pluseY[i].gpioOn=0;
				pluseY[i].gpioOff=1<<YS;
				pluseY[i].usDelay=timing;

				dirY[i].gpioOn=1<<YD;
				dirY[i].gpioOff=0;
				dirY[i].usDelay=timing;
			}
		}
		else if(bh2==3)
		{
			for(i=0;i<steps;i++)
			{
				pluseY[i].gpioOn=1<<YS;
				pluseY[i].gpioOff=0;
				pluseY[i].usDelay=timing;

				dirY[i].gpioOff=1<<YD;
				dirY[i].gpioOn=0;
				dirY[i].usDelay=timing;
				i++;
				pluseY[i].gpioOn=0;
				pluseY[i].gpioOff=1<<YS;
				pluseY[i].usDelay=timing;

				dirY[i].gpioOff=1<<YD;
				dirY[i].gpioOn=0;
				dirY[i].usDelay=timing;
			}
		}
		else if(bh2 == 0)
		{
			for(i=0;i<steps;i++)
			{
				pluseY[i].gpioOn=1<<YS;
				pluseY[i].gpioOff=0;
				pluseY[i].usDelay=timing;

				dirY[i].gpioOff=1<<YD;
				dirY[i].gpioOn=0;
				dirY[i].usDelay=timing;
				i++;
				pluseY[i].gpioOff=0;
				pluseY[i].gpioOn=1<<YS;
				pluseY[i].usDelay=timing;

				dirY[i].gpioOff=1<<YD;
				dirY[i].gpioOn=0;
				dirY[i].usDelay=timing;
			}


		}
		if(*b == 16)
		{
			exit(0);
		}
		gpioWaveAddGeneric(steps, pluseX); 
		gpioWaveAddGeneric(steps, pluseY); 
		gpioWaveAddGeneric(steps, dirX);
		gpioWaveAddGeneric(steps, dirY);
		wid = gpioWaveCreate();
		wstp[0]=wid;
		while (gpioWaveTxBusy());
		gpioWaveChain(wstp,1);
		while (gpioWaveTxBusy());
		gpioWaveClear();
		while (gpioWaveTxBusy());
		//	gpioTerminate();
	}
}

