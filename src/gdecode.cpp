/* strcspn example */
#include <iostream>
#include <string.h>
#include <fstream>
#include <cstdlib>
#include <cmath>
#include <iomanip>
#include <utility>

#include"gconfig.h"
using namespace std;

const double PI = 3.141592653589793;

struct gcode
{
	int code;
	float X;
	float Y;
	float I;
	float J;
};
struct velocity
{
	double xS , xE;
	double yS , yE;
};
gcode getg(string strin)
{
	char str[40];
	char gs[10];
	char xs[10];
	char ys[10];
	char Is[10];
	char Js[10];
	int i,w;
	gcode g;

	strncpy( str,strin.c_str(), sizeof(str));
	puts(str);

	i = strcspn (str,"G");
	w = strcspn (str+i+1," ");
	strncpy(gs,str+i+1,w);
	gs[w] = '\0';   /* null character manually added */
	g.code=atoi(gs);

	i = strcspn (str,"X");
	w = strcspn (str+i+1," ");
	strncpy(xs,str+i+1,w);
	xs[w] = '\0';   /* null character manually added */
	g.X=atof(xs);

	i = strcspn (str,"Y");
	w = strcspn (str+i+1," ");
	strncpy(ys,str+i+1,w);
	ys[w] = '\0';   /* null character manually added */
	g.Y=atof(ys);

	i = strcspn (str,"I");
	w = strcspn (str+i+1," ");
	strncpy(Is,str+i+1,w);
	Is[w] = '\0';   /* null character manually added */
	g.I=atof(Is);

	i = strcspn (str,"J");
	w = strcspn (str+i+1," ");
	strncpy(Js,str+i+1,w);
	Js[w] = '\0';   /* null character manually added */
	g.J=atof(Js);

	return g;
}
velocity getv(gcode gin)
{
	velocity gv;
	float speed = gin.code?SPEED_N:SPEED_R;

	if((gin.code==0)|(gin.code==1))
	{
		float D=sqrt(gin.X*gin.X+gin.Y*gin.Y);
		gv.xS=(gin.X/D)*speed;
		gv.yS=(gin.Y/D)*speed;
		gv.xE=(gin.X/D)*speed;
		gv.yE=(gin.Y/D)*speed;

	}
	else if((gin.code==2)|(gin.code==3))
	{
		float R=  sqrt((gin.X-gin.I)*(gin.X-gin.I)+(gin.Y-gin.J)*(gin.Y-gin.J));
		float Dc= sqrt(gin.I*gin.I+gin.J*gin.J);
		float Rt= (1 - (R/Dc));
		float x0= gin.I*Rt;
		float y0= gin.J*Rt;
		float D=  sqrt(x0*x0+y0*y0);
		float T=  2*PI*R/speed;
		int ArcDir;
		if(gin.code==2)
			ArcDir  =-1; //Clock Wise
		else
			ArcDir  =1;  // Anti Clock Wise


		double taS = R*acos((x0-gin.I)/R)/speed;
		if((ArcDir*(y0-gin.J))<0)
			taS=T-taS;

		double taE = R*acos((gin.X-gin.I)/R)/speed;
		if((ArcDir*(gin.Y-gin.J))<0)
			taE=T-taE;
		if(taE<taS)
			taE=taE+T;

		double  phaseS=((speed/R)*taS);
		double  phaseE=((speed/R)*taE);
		gv.xS = -speed*sin(phaseS);
		gv.yS = ArcDir*speed*cos(phaseS);

		gv.xE = -speed*sin(phaseE);
		gv.yE = ArcDir*speed*cos(phaseE);

		if(D>3)
		{
			gv.xS = x0*speed/D;
			gv.yS = y0*speed/D;
		}
	}
	return gv;
}
double getA( velocity v, velocity vf, float speed)
{
	double alpha,ax=1,ay=1;
	if(KX==1)
		ax = SPEED_DIF_X/abs(vf.xS - v.xE);
	else if(vf.xS != v.xE )
		ax = abs(sqrt(1+( (4*abs(v.xE)*(KX-1)*SPEED_DIF_X)/(speed*abs(vf.xS - v.xE ))))-1)/((2*abs(v.xE)*(KX-1)/speed));
	else
		ax=1;
	if(KY==1)
		ay = SPEED_DIF_Y/abs(vf.yS - v.yE);
	else if(vf.yS != v.yE )
		ay = abs(sqrt(1+( (4*abs(v.yE)*(KY-1)*SPEED_DIF_Y)/(speed*abs(vf.yS - v.yE ))))-1)/((2*abs(v.yE)*(KY-1)/speed));
	else
		ay=1;
	alpha = ax>ay?ay:ax;
	alpha = alpha>1?1:alpha;
	return alpha;
}
double fovx(double u)
{
	double diff = SPEED_DIF_X/((u/SPEED_N)*(KX - 1)+ 1) ;
	return diff;
}
double fovy(double u)
{
	double diff = SPEED_DIF_Y/((u/SPEED_N)*(KY - 1)+ 1) ;
	return diff;
}

double nxtx(double p0,double p1)
{
	double d=SPEED_DIF_X;
	d=fovx(abs(p0));
	int dirp0 = p0>=0?1:-1;
	bool cond =(abs(p1)-abs(p0))<=d;
	if (cond)
		return p1;
	else
		return dirp0*(abs(p0)+d);
}
double nxty(double p0,double p1)
{
	double d=SPEED_DIF_Y;
	d=fovy(abs(p0));
	int dirp0 = p0>=0?1:-1;
	bool cond =(abs(p1)-abs(p0))<=d;
	if (cond)
		return p1;
	else
		return dirp0*(abs(p0)+d);
}
template <int N> void filt(double iox[N], double ioy[N] , double iot[N] ,char steps[N], int timeC[N] )
{
	double out, outx, outy, aoutx, aouty;
	static double buffx_1[N], buffx_2[N];
	static double buffy_1[N], buffy_2[N];
	static double abuffx_1[N], abuffx_2[N];
	static double abuffy_1[N], abuffy_2[N];
	static double abufft_1[N], abufft_2[N];
	static char asteps_1[N], asteps_2[N];

	static double outf=1;
	int scale = 1000;
	double temp;

	for(int i=0; i<N; i++)
	{
		temp = iox[i];
		buffx_2[i] = temp;
		abuffx_2[i] = temp;

		temp = ioy[i];
		buffy_2[i] = temp;
		abuffy_2[i] = temp;

		temp = iot[i];
		abufft_2[i] = temp;

		asteps_2[i] = steps[i];

	}

	std::swap(buffx_1, buffx_2);
	std::swap(abuffx_1, abuffx_2);
	std::swap(buffy_1, buffy_2);
	std::swap(abuffy_1, abuffy_2);
	std::swap(abufft_1, abufft_2);
	std::swap(asteps_1, asteps_2);

	//in descending time
	for(int i=N-1;i>0;i--)
	{
		buffx_1[i-1]=nxtx(buffx_1[i],buffx_1[i-1]);
		buffy_1[i-1]=nxty(buffy_1[i],buffy_1[i-1]);
	}
	buffx_2[N-1]=nxtx(buffx_1[0],buffx_2[N-1]);
	buffy_2[N-1]=nxty(buffy_1[0],buffy_2[N-1]);

	for(int i=N-1;i>0;i--)
	{
		buffx_2[i-1]=nxtx(buffx_2[i],buffx_2[i-1]);
		buffy_2[i-1]=nxty(buffy_2[i],buffy_2[i-1]);
	}
	//In ascending time
	for(int i=1;i<N;i++)
	{
		buffx_2[i]= nxtx(buffx_2[i-1], buffx_2[i]);
		buffy_2[i]= nxty(buffy_2[i-1], buffy_2[i]);
	}
	buffx_1[0]= nxtx(buffx_2[N-1], buffx_1[0]);
	buffy_1[0]= nxty(buffy_2[N-1], buffy_1[0]);

	for(int i=0;i<N;i++)
	{
		double mag = sqrt(buffx_2[i]*buffx_2[i]+buffy_2[i]*buffy_2[i]);
		outx=buffx_2[i];
		outy=buffy_2[i];
		aoutx=abuffx_2[i];
		aouty=abuffy_2[i];

		outx=(abs(outx)>1/MAXT)?outx:1/MAXT*buffx_2[i]/mag;
		outy=(abs(outy)>1/MAXT)?outy:1/MAXT*buffy_2[i]/mag;
		double Rx = abs(aoutx)<=2? 1:abs((outx)/(aoutx));
		double Ry = abs(aouty)<=2? 1:abs((outy)/(aouty));
		out = Rx<Ry?Rx:Ry;
		outf = (out!=0)?1/out:outf;

		timeC[i] = (int)((abufft_2[i]*outf)*scale) ;
		steps[i] = asteps_2[i];
	}
};

template< int id >
class buff{
	double gtimX[FL];
	double gtimY[FL];
	double gtimT[FL];
	char steps[FL];
	int address;
	ofstream gs;
	ofstream gt;
	bool first_done;

	public:
	bool write_buff(double gX,double gY,double gt, char step);
	bool full_check();
	//void reset();
	bool get_tc();
	void flush();
	buff();
};
	template< int id >
bool buff<id>::get_tc()
{
	int timeC[FL];
	filt<FL>(gtimX,gtimY,gtimT,steps, timeC);
	if(first_done)
	{
		for(int k=0;k<FL;k++)
		{
			if(steps[k]!='E')
			{
				gt<<timeC[k]<<endl;
				gs<<steps[k]<<endl;
			}
			else
			{
				if(steps[k]=='E')
					return 0;
			}
		}
	}
	else
		first_done = 1;
	return 1;
};
	template< int id >
bool buff<id>::write_buff( double gX, double gY, double gT, char sp)
{
	bool b_active;
	gtimX[address]=gX;
	gtimY[address]=gY;
	gtimT[address]=gT;
	steps[address]=sp;
	address++;

	bool full = full_check();
	if(full)
		b_active=get_tc();
	else
		b_active=true;
	return b_active;
}
	template< int id >
bool buff<id>::full_check()
{
	if(address==FL)
	{
		address=0;
		return 1;
	}
	else
	{
		return 0;
	}
}
	template< int id >
void buff<id>::flush()
{
	while(write_buff(0,0,5,'E'));
};
	template< int id >
buff<id>::buff()
{
	char idc[5]="1";
	//@TODO
	//itoa(id,idc,10);
	string names="./motion/step";
	names.append(idc);
	names.append(".txt");
	string namet="./motion/time";
	namet.append(idc);
	namet.append(".txt");

	gs.open(names.c_str());
	gt.open(namet.c_str());
	for (int i = 0; i<FL; i++ )
	{
		gtimX[FL]=0;
		gtimY[FL]=0;
		gtimT[FL]=0;
	}
	address=0;

	first_done = 0;
};

void g2rg()
{
	ifstream fgcode;
	ofstream frgcode;
	fgcode.open("./gcode/agcode.txt");
	frgcode.open("./gcode/gcode.txt");
	string strin="";
	gcode g;
	int n=0;
	char out_g[100];
	float absX=0, absY=0;
	//ostringstream og;
	while(!fgcode.eof())
	{
		getline(fgcode,strin);
		g=getg(strin);
		int   	code=g.code;
		float	X	=g.X;
		float	Y	=g.Y;
		float	I	=g.I;
		float	J	=g.J;
		n=0;
		if((g.code==0)||(g.code==1))
		{
			if(!((X==absX)&&(Y==absY)))
			{
				n=sprintf(out_g,"G%d X%f Y%f ",code, X-absX,Y-absY);
				frgcode.write(out_g,n);
				frgcode.write("\n",1);
			}
		}
		else if((g.code==2)||(g.code==3) )
		{
			if(((X==absX)&&(Y==absY))&&(!((I==0)&&(J==0))))
			{
				n=sprintf(out_g,"G%d X%f Y%f I%f J%f",code,2*I,2*J, I, J);
				frgcode.write(out_g,n);
				frgcode.write("\n",1);
				n=sprintf(out_g,"G%d X%f Y%f I%f J%f",code,-2*I,-2*J, -I, -J);
				frgcode.write(out_g,n);
				frgcode.write("\n",1);
			}
			else
			{
				n=sprintf(out_g,"G%d X%f Y%f I%f J%f",code,X-absX,Y-absY, I, J);
				frgcode.write(out_g,n);
				frgcode.write("\n",1);
			}
		}
		absX=g.X;
		absY=g.Y;
	}
	frgcode.write("END",3);
	frgcode.close();
	fgcode.close();
};


void mdecode()
{
	ifstream fgcode;
	fgcode.open("./gcode/gcode.txt");

	string strin="";
	gcode g, gf;
	velocity  vf,v;

	int code=0;

	const double PI = 3.141592653589793;
	double x1, I;
	double y1, J;

	static buff<1> buffer;
	static int count=0;

	double speed;
	bool stpdx=0,stpdy=0, dircx=1, dircy=1;
	double step = SX>SY?SY:SX;
	double stepX=0,stepY=0;
	char stepcode='9';

	bool file_done=0;
	getline(fgcode,strin);
	g=getg(strin);

	float Alpha1=0, Alpha2=1;
	double xoff=0, yoff=0;
	double xoffb=0, yoffb=0;
	double ttime=0;
	while(!file_done)
	{
		getline(fgcode,strin);
		gf=getg(strin);
		speed = g.code?SPEED_N:SPEED_R;
		v  = getv(g);
		vf = getv(gf);

		Alpha2 = getA(v,vf,speed);

		if(!fgcode.eof())
		{
			code=g.code;
			x1=g.X;
			y1=g.Y;
			I=g.I;
			J=g.J;
		}
		else
		{
			code=g.code;
			x1=g.X;
			y1=g.Y;
			I=g.I;
			J=g.J;
			Alpha2=0;
		}

		stepX=0;
		stepY=0;
		dircx=0;
		dircy=0;

		//Scaling gcode	
		x1=x1*SCALE;
		y1=y1*SCALE;
		I=I*SCALE;
		J=J*SCALE;

		//linear ARC
		ttime=0;
		xoff=xoffb;
		yoff=yoffb;
		if((code == 0)||(code == 1))
		{
			double T,t=0,ts;
			double D,x,y,vx,vy;
			D=sqrt(x1*x1+y1*y1);
			T=D/speed;
			ts=(step/(speed*FINE));
			vx=v.xS;
			vy=v.yS;
			if(code== 0)
				buffer.write_buff(Alpha1*vx,Alpha1*vy,-1,'0');
			else
				buffer.write_buff(Alpha1*vx,Alpha1*vy,-1,'9');

			for (t=0;t<=T;t=t+ts)
			{
				stpdx=0;
				stpdy=0;
				x=(x1/D)*speed*t+xoff;
				y=(y1/D)*speed*t+yoff;
				vx = x1*speed/D;
				vy = y1*speed/D;

				if(abs(x-stepX)>(SX))
				{
					xoffb=0;
					stpdx=1;
					dircx=(x>stepX);
					if(dircx)
						stepX+=SX;
					else
						stepX-=SX;

				}
				if(abs(y-stepY)>(SY))
				{
					yoffb=0;
					stpdy=1;
					dircy=(y>stepY);
					if(dircy)
						stepY+=SY;
					else
						stepY-=SY;

				}

				stepcode='0';
				if(stpdx|stpdy)
				{
					yoffb=(y-stepY);
					xoffb=(x-stepX);
					if((stpdx==0)&&(stpdy==0))
						stepcode='0';

					if((stpdx==1)&&(stpdy==0))
						stepcode=dircx?'1':'5';

					if((stpdx==0)&&(stpdy==1))
						stepcode=dircy?'3':'7';

					if((stpdx==1)&&(stpdy==1))
						stepcode=dircx==dircy?(dircx?'2':'6'):(dircy?'4':'8');

					Alpha1=1;
					buffer.write_buff(vx,vy,ttime, stepcode);

					count++;
					ttime=0;
				}
				ttime+=ts;
			}
			vx=v.xE;
			vy=v.yE;
			buffer.write_buff(Alpha2*vx,Alpha2*vy,-1,'9');
		}
		//Circular ARC
		if((code == 2)||(code == 3))
		{
			double T, T1,t=0, ts;
			double D, Dc, R, Rt, x, y, vx, vy;
			double x0,y0;
			//bool ArcMinor;
			int ArcDir;
			R=  sqrt((x1-I)*(x1-I)+(y1-J)*(y1-J));
			Dc= sqrt(I*I+J*J);
			Rt= (1 - (R/Dc));
			x0= I*Rt;
			y0= J*Rt;
			D=  sqrt(x0*x0+y0*y0);
			cout<<x0<<", "<<y0<<", D = "<<D<<endl;
			if(code==2)//CW
				ArcDir  =-1;
			else
				ArcDir  =1;

			T1= D/speed;
			T=  2*PI*R/speed;
			ts= (step/(speed*FINE));

			vx=v.xS;
			vy=v.yS;
			//LINE
			buffer.write_buff(Alpha1*vx,Alpha1*vy,-1,'9');

			if(D>3)
			{
				for (t=0;t<=T1;t=t+ts)
				{
					stpdx=0;
					stpdy=0;
					x=(x0/D)*speed*t;
					y=(y0/D)*speed*t;
					vx = x0*speed/D;
					vy = y0*speed/D;

					if(abs(x-stepX)>(SX))
					{
						stpdx=1;
						dircx=(x>stepX);
						if(dircx)
							stepX+=SX;
						else
							stepX-=SX;
					}
					if(abs(y-stepY)>(SY))
					{
						stpdy=1;
						dircy=(y>stepY);
						if(dircy)
							stepY+=SY;
						else
							stepY-=SY;
					}
					stepcode='0';
					if(stpdx|stpdy)
					{
						if((stpdx==0)&&(stpdy==0))
							stepcode='0';

						if((stpdx==1)&&(stpdy==0))
							stepcode=dircx?'1':'5';

						if((stpdx==0)&&(stpdy==1))
							stepcode=dircy?'3':'7';

						if((stpdx==1)&&(stpdy==1))
							stepcode=dircx==dircy?(dircx?'2':'6'):(dircy?'4':'8');

						buffer.write_buff(vx,vy,ttime, stepcode);

						ttime=0;
						count++;
					}
					ttime+=ts;
				}
				buffer.write_buff(0,0,-1,'9');
			}
			//Arc
			ts= (step/(speed*FINE));
			double tS=0,tE=0;
			cout<<"Find Circle"<<endl;
			double theS=((x0-I)/R);
			double theE=((x1-I)/R);
			theS=theS<-1?-1:(theS>1?1:theS);
			theE=theE<-1?-1:(theE>1?1:theE);
			double taS = R*acos(theS)/speed;
			if((ArcDir*(y0-J))<0)
				taS=T-taS;

			double taE = R*acos(theE)/speed;
			if((ArcDir*(y1-J))<0)
				taE=T-taE;
			if(taE<taS)
				taE=taE+T;
			cout<<"TS= "<<taS<<" TE= "<<taE<<endl; 
			tS=taS;
			tE=taE;
			cout<<"Implimenting Circle of radius = "<<R<<endl;
			ttime=0;
			for (t=tS;t<=tE;t=t+ts)
			{
				stpdx=0;
				stpdy=0;
				double  phase=((speed/R)*t);
				x=  R*cos(phase)+I;
				y=  ArcDir*R*sin(phase)+J;
				vx = -speed*sin(phase);
				vy = ArcDir*speed*cos(phase);

				if(abs(x-stepX)>(SX))
				{
					stpdx=1;
					dircx=(x>stepX);
					if(dircx)
						stepX+=SX;
					else
						stepX-=SX;
				}
				if(abs(y-stepY)>(SY))
				{
					stpdy=1;
					dircy=(y>stepY);
					if(dircy)
						stepY+=SY;
					else
						stepY-=SY;
				}
				stepcode='0';
				if(stpdx|stpdy)
				{
					if((stpdx==1)&&(stpdy==0))
						stepcode=dircx?'1':'5';

					if((stpdx==0)&&(stpdy==1))
						stepcode=dircy?'3':'7';

					if((stpdx==1)&&(stpdy==1))
						stepcode=dircx==dircy?(dircx?'2':'6'):(dircy?'4':'8');

					buffer.write_buff(vx,vy,ttime, stepcode);

					ttime=0;
					count++;
				}
				ttime+=ts;
			}
			vx=v.xE;
			vy=v.yE;
			buffer.write_buff(Alpha2*vx,Alpha2*vy,-1, '9');
		}

		g=gf;

		Alpha1=Alpha2;

		if(fgcode.eof())
			file_done=1;
	}
	buffer.flush();
};

int main ()
{
	mdecode();
	return 0;
}
