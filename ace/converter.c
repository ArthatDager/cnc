#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <malloc.h>
#include "converter.h"
#include "ace.h"
struct layer_obj *layer ;
struct priority_obj *priority ;
struct convert_obj convertop ;
int iLayerCount, iPrioCount;
char szDxfFile[MPATH], szToFileName[MPATH];
int precision=3;
int demo=0;

int get_values(FILE *, struct entity_obj *);
int get_string(FILE *, const char *, char *);
void get_first_point(double *, double *, double *, struct entity_obj *);
void get_second_point(double *, double *, double *, struct entity_obj *);
void make_arc(struct entity_obj *);
double min(double, double);
int DelPriority (int, int);
int NewPriority (int);
int ReadLayer (char *);
void GetOption(char, char *);
void SaveOption(char, char *);
char *current_directory(char *path);
int check_key(char *, char *);
void convert(void);

char szAppName[]="ACEConverter";
char szAcePath[50];
double defaultzoffset=-1.5;
double defaultmaxzpass=100;
double defaultreleaseplane=30;
double defaultcloseenough=0.01;
int defaultpriorityoptimization=0;

struct layer_obj *temp_lay ;
struct priority_obj *temp_pri ;
int main()
{
     static char szTitleName[50] ;
     static char szDrive[50], szDir[50], szName[50], szExt[50] ;
     static char szDXFFilter[]="DXF Files (*.DXF)\0*.dxf\0" ;
     static char szNCFilter[]="NC Files (*.NC)\0*.nc\0" ;
     static char szString[50], status[100], szFileName[50];
     static char szHelp[50], szDirectory[50] ;
     static char szPrecision;
     static char *conversionend;
     static int i, iID;
     //static HINSTANCE hInstance ;
     //static OPENFILENAME ofn ;
     static char inpfilepath[50]="test.dxf"  ;
     static char outfilepath[50]="test.nc"  ;
     
     sprintf(szDxfFile,"%s",inpfilepath); 
     sprintf(szToFileName,"%s",outfilepath); 
     GetOption('4',&szPrecision);

     iLayerCount=ReadLayer (inpfilepath) ;
     if(iLayerCount>0)
     {
         iPrioCount=NewPriority (iPrioCount) ;
         for(i=0;i<iLayerCount;i++)
         {
             sprintf(szString,"%s...%d",layer[i].name,layer[i].priority);
             puts(szString);
         }
         //CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE) convert,	NULL,	0,	&iID);
         convert();
     } 
return 0;
}

//void WINAPI convert(void)
void convert(void)
{
   int ctemp, zchar, wchar, achar, cchar, count=0, closed, msg=0;
   long i, lay_index, k, j, l, temp, num_of_ent, line_num=1, cur_ent, cur_dir, delay, display;
   double x1, y1, z1, ztemp, x2, y2, z2, dist1, dist2, cur_dist, zref, x1st=0, y1st=0, z1st=0;
   static char string[100], type[100], status[100];
   static struct entity_obj temp_ent, temp_ent2;
   static struct entity_obj *entity;
   FILE *ifp, *ofp;
   fpos_t pos;

   sprintf(status,"Begin Converting Process");
   //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
    printf("%s",status );
   if((ifp=fopen(szDxfFile,"r"))==NULL)
     {sprintf(status,"Invalid .dxf File Format");
      //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
      printf("%s",status );
      return;
     }
   if((ofp=fopen(szToFileName,"w"))==NULL)
     {fclose(ifp);
      sprintf(status,"Invalid Output File");
      //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
      printf("%s",status );
      return;
     }

   if((entity=(struct entity_obj *)calloc(1,sizeof(struct entity_obj)))==NULL) {msg=2; goto DONE;}
   for(i=0;i<iPrioCount;i++)
     {//alocate and store entities
      num_of_ent=0; display=100;
      while(1)
        {if((temp=fscanf(ifp,"%s",string))==0 || temp==EOF) break;
         if(strcmp(string,"0")!=0) continue;
         fgetpos(ifp,&pos);
         if((temp=fscanf(ifp,"%s",type))==0 || temp==EOF) break;
         if(num_of_ent>=display)
           {display=num_of_ent+100;
            sprintf(status,"Stored %u Ent., Prio. %u",num_of_ent,i+1);
            //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
           }
         if(strcmp(type,"LINE")==0 || strcmp(type,"CIRCLE")==0 ||
            strcmp(type,"ARC")==0 || strcmp(type,"POINT")==0 || strcmp(type,"POLYLINE")==0)
           {if(get_string(ifp,"8",string)==0) {msg=1; goto DONE;}
            for(lay_index=0;lay_index<iLayerCount;lay_index++)
               if(strcmp(layer[lay_index].name,string)==0 &&
                  layer[lay_index].priority-1==i &&
                  layer[lay_index].status==1) break;
            if(lay_index==iLayerCount) continue;
            if(strcmp(type,"POLYLINE")!=0)
              {
                  if((entity=(struct entity_obj *)realloc(entity,(++num_of_ent)*sizeof(struct entity_obj)))==NULL) {msg=2; goto DONE;}
              }
           }
         else if(strcmp(type,"BLOCK")==0)
           {while(1)
              {if((temp=fscanf(ifp,"%s",string))==0 || temp==EOF) {msg=1; goto DONE;}
               if(strcmp(string,"0")==0)
                 {fgetpos(ifp, &pos);
                  if((temp=fscanf(ifp,"%s",string))==0 || temp==EOF) {msg=1; goto DONE;}
                  if(strcmp(string,"ENDBLK")==0) break;
                  else fsetpos(ifp, &pos);
                 }
              }
            continue;
           }
         else
           {fsetpos(ifp,&pos);
            continue;
           }
         if(strcmp(type,"POLYLINE")==0)
           {delay=zref=0;
            if((temp=get_values(ifp,&temp_ent2))==0) {msg=1; goto DONE;}
            if(temp==2) closed=1;
            else closed=0;
            zref=temp_ent2.z1;
            while((temp=fscanf(ifp,"%s",string))!=EOF && temp!=0)
              {if(strcmp(string,"SEQEND")==0 && closed==0) break;
               if(strcmp(string,"VERTEX")==0 || (strcmp(string,"SEQEND")==0 && closed==1))
                 {if(strcmp(string,"SEQEND")==0 && closed==1)
                    {temp_ent.x2=x1st; temp_ent.y2=y1st; temp_ent.z2=z1st;
                    }
                  else
                    {if(get_values(ifp,&temp_ent2)==0) {msg=1; goto DONE;}
                     temp_ent.x2=temp_ent2.x1;
                     temp_ent.y2=temp_ent2.y1;
                     temp_ent.z2=temp_ent2.z1+zref;
                    }
                  if(delay>0)
                    {
                        if((entity= (struct entity_obj *)realloc(entity,(++num_of_ent)*sizeof(struct entity_obj)))==NULL) {msg=2; goto DONE;}
                     entity[num_of_ent-1]=temp_ent;
                     if(entity[num_of_ent-1].type==ARC) make_arc(&entity[num_of_ent-1]);
                     entity[num_of_ent-1].layer=lay_index;

                     if(entity[num_of_ent-1].type==LINE)
                       {entity[num_of_ent-1].dir=FOR;
                        entity[num_of_ent-1].z1=entity[num_of_ent-1].z1+layer[lay_index].zoffset;
                        entity[num_of_ent-1].z2=entity[num_of_ent-1].z2+layer[lay_index].zoffset;
                        for(k=1;k*-layer[lay_index].depth>min(entity[num_of_ent-1].z1,entity[num_of_ent-1].z2);k++)
                          {
                              if((entity=(struct entity_obj *)realloc(entity,(++num_of_ent)*sizeof(struct entity_obj)))==NULL) {msg=2; goto DONE;}
                           entity[num_of_ent-1]=entity[num_of_ent-2];
                           if(entity[num_of_ent-2].z1<k*-layer[lay_index].depth) entity[num_of_ent-2].z1=k*-layer[lay_index].depth;
                           if(entity[num_of_ent-2].z2<k*-layer[lay_index].depth) entity[num_of_ent-2].z2=k*-layer[lay_index].depth;
                          }
                       }
                     if(entity[num_of_ent-1].type==ARC)
                       {entity[num_of_ent-1].z1=entity[num_of_ent-1].z1+layer[lay_index].zoffset;
                        if(layer[lay_index].arc==IDD_CCWARC || layer[lay_index].arc==IDD_EITHERARC) entity[num_of_ent-1].dir=CCW;
                        else entity[num_of_ent-1].dir=CW;
                        for(k=1;k*-layer[lay_index].depth>entity[num_of_ent-1].z1;k++)
                          {
                              if((entity=(struct entity_obj *)realloc(entity,(++num_of_ent)*sizeof(struct entity_obj)))==NULL) {msg=2; goto DONE;}
                           entity[num_of_ent-1]=entity[num_of_ent-2];
                           if(entity[num_of_ent-2].z1<k*-layer[lay_index].depth) entity[num_of_ent-2].z1=k*-layer[lay_index].depth;
                          }
                       }
                    }
                  else
                    {delay++;
                     x1st=temp_ent.x2; y1st=temp_ent.y2; z1st=temp_ent.z2;
                    }
                  if(strcmp(string,"SEQEND")==0 && closed==1) break;
                  temp_ent.radius=temp_ent2.radius;
                  if(temp_ent.radius!=0) temp_ent.type=ARC;
                  else temp_ent.type=LINE;
                  temp_ent.x1=temp_ent.x2;
                  temp_ent.y1=temp_ent.y2;
                  temp_ent.z1=temp_ent.z2;
                 }
              }
            if(temp==EOF || temp==0) break;
            continue;
           }
         if(strcmp(type,"LINE")==0 || strcmp(type,"POINT")==0)
           {if(strcmp(type,"LINE")==0) entity[num_of_ent-1].type=LINE;
            else entity[num_of_ent-1].type=POINT;
            entity[num_of_ent-1].layer=lay_index;
            if(strcmp(type,"LINE")==0) entity[num_of_ent-1].dir=FOR;
            if(get_values(ifp,&entity[num_of_ent-1])==0) {msg=1; goto DONE;}
            entity[num_of_ent-1].z1=entity[num_of_ent-1].z1+layer[lay_index].zoffset;
            if(strcmp(type,"LINE")==0) entity[num_of_ent-1].z2=entity[num_of_ent-1].z2+layer[lay_index].zoffset;
            
            for(k=1;k*-layer[lay_index].depth>min(entity[num_of_ent-1].z1,entity[num_of_ent-1].z2);k++)
              {
                 if((entity=(struct entity_obj *)realloc(entity,(++num_of_ent)*sizeof(struct entity_obj)))==NULL) {msg=2; goto DONE;}
               entity[num_of_ent-1]=entity[num_of_ent-2];
               if(entity[num_of_ent-2].z1<k*-layer[lay_index].depth) entity[num_of_ent-2].z1=k*-layer[lay_index].depth;
               if(entity[num_of_ent-2].z2<k*-layer[lay_index].depth) entity[num_of_ent-2].z2=k*-layer[lay_index].depth;
              }
            continue;
           }
         if(strcmp(type,"ARC")==0 || strcmp(type,"CIRCLE")==0)
           {entity[num_of_ent-1].type=ARC;
            entity[num_of_ent-1].layer=lay_index;
            if(layer[lay_index].arc==IDD_CCWARC || layer[lay_index].arc==IDD_EITHERARC) entity[num_of_ent-1].dir=CCW;
            else entity[num_of_ent-1].dir=CW;
            if(get_values(ifp,&entity[num_of_ent-1])==0) {msg=1; goto DONE;}
            entity[num_of_ent-1].z1=entity[num_of_ent-1].z1+layer[lay_index].zoffset;
            if(strcmp(type,"ARC")==0)
              {entity[num_of_ent-1].ang_start=entity[num_of_ent-1].ang_start*2*PI/360;
               entity[num_of_ent-1].ang_end=entity[num_of_ent-1].ang_end*2*PI/360;
              }
            else
              {entity[num_of_ent-1].ang_start=0;
               entity[num_of_ent-1].ang_end=2*PI;
              }

            for(k=1;k*-layer[lay_index].depth>entity[num_of_ent-1].z1;k++)
              {
                  if((entity=(struct entity_obj *)realloc(entity,(++num_of_ent)*sizeof(struct entity_obj)))==NULL) {msg=2; goto DONE;}
               entity[num_of_ent-1]=entity[num_of_ent-2];
               if(entity[num_of_ent-2].z1<k*-layer[lay_index].depth) entity[num_of_ent-2].z1=k*-layer[lay_index].depth;
              }
            continue;
           }
         }
      rewind(ifp);

      //optimize if necessary
      if(priority[i].optimize==1)
        {x1=y1=0; z1=priority[i].release; display=100;
         for(j=0;j<num_of_ent;j++)
           {if(j+1==display)
              {display=display+100;
               sprintf(status,"Optimizing Prio. %u, %d%% Complete",i+1, (int)(j+1)*100/num_of_ent);
               //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
               printf("%s",status );
              }
            for(k=j;k<num_of_ent;k++)
              {if(entity[k].type==ARC && layer[entity[k].layer].arc==IDD_CCWARC)
                 {get_first_point(&x2, &y2, &z2, &entity[k]);
                  dist1=sqrt(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2));
                  if(j==k) cur_dist=dist1;
                  if(dist1<cur_dist) {cur_ent=k; cur_dir=CCW; cur_dist=dist1;}
                 }
               else if(entity[k].type==ARC && layer[entity[k].layer].arc==IDD_CWARC)
                 {get_second_point(&x2, &y2, &z2, &entity[k]);
                  dist1=sqrt(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2));
                  if(j==k) cur_dist=dist1;
                  if(dist1<=cur_dist) {cur_ent=k; cur_dir=CW; cur_dist=dist1;}
                 }
               else if(entity[k].type==ARC)
                 {get_first_point(&x2, &y2, &z2, &entity[k]);
                  dist1=sqrt(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2));
                  get_second_point(&x2, &y2, &z2, &entity[k]);
                  dist2=sqrt(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2));
                  if(j==k) cur_dist=min(dist1,dist2);
                  if(dist1<=cur_dist) {cur_ent=k; cur_dir=CCW; cur_dist=dist1;}
                  if(dist2<=cur_dist) {cur_ent=k; cur_dir=CW; cur_dist=dist2;}
                 }
               else if(entity[k].type==LINE)
                 {get_first_point(&x2, &y2, &z2, &entity[k]);
                  dist1=sqrt(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2));
                  get_second_point(&x2, &y2, &z2, &entity[k]);
                  dist2=sqrt(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2));
                  if(j==k) cur_dist=min(dist1, dist2);
                  if(dist1<=cur_dist)
                   {cur_ent=k; cur_dir=FOR; cur_dist=dist1;}
                  if(dist2<=cur_dist) {cur_ent=k; cur_dir=REV; cur_dist=dist2;}
                 }
               else if(entity[k].type==POINT)
                 {get_first_point(&x2, &y2, &z2, &entity[k]);
                  dist1=sqrt(pow(x2-x1,2)+pow(y2-y1,2)+pow(z2-z1,2));
                  if(j==k) cur_dist=dist1;
                  if(dist1<=cur_dist) {cur_ent=k; cur_dir=REV; cur_dist=dist1;}
                 }
              }
             entity[cur_ent].dir=cur_dir;
             temp_ent=entity[j]; entity[j]=entity[cur_ent]; entity[cur_ent]=temp_ent;
             get_second_point(&x1, &y1, &ztemp, &entity[j]);
           }
        }

      //write precode to file
      if(demo==0 || (demo==1 && count<=20))
        {fprintf(ofp,"%s",priority[i].precode);
         if(strlen(priority[i].precode)>0 &&
            priority[i].precode[strlen(priority[i].precode)-1]!='\n') fputc('\n',ofp);
        }
      //write code to file
      display=100;
      for(k=0;k<num_of_ent;k++)
         {//entity overhead
          if(k+1==display)
            {display=display+100;
             sprintf(status,"Writing Prio. %u, %d%% Complete",i+1, (int)(k+1)*100/num_of_ent);
             //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
             printf("%s",status );
            }
          if(demo==1) {if(count<=20) count++; if(count>20) break;}
          get_first_point(&x2, &y2, &z2, &entity[k]);
          if(k==0) {x1=x2; y1=y2; z1=z2; ctemp=layer[entity[k].layer].zchar;}
          dist1=sqrt(pow(x2-x1,2)+pow(y2-y1,2));
          if(dist1>priority[i].close || k==0 || entity[k].type==POINT || ctemp!=layer[entity[k].layer].zchar)
            {if(k==0)
               {zchar=wchar=achar=cchar=0;
                for(l=0;l<num_of_ent;l++)
                  {if(layer[entity[l].layer].zchar=='Z') zchar=1;
                   if(layer[entity[l].layer].zchar=='W') wchar=1;
                   if(layer[entity[l].layer].zchar=='A') achar=1;
                   if(layer[entity[l].layer].zchar=='C') cchar=1;
                  }

//Added .4 formatter spec

                if(zchar==1) fprintf(ofp,"G00 Z%.*f\n",precision,priority[i].release);
                if(wchar==1) fprintf(ofp,"G00 W%.*f\n",precision,priority[i].release);
                if(achar==1) fprintf(ofp,"G00 A%.*f\n",precision,priority[i].release);
                if(cchar==1) fprintf(ofp,"G00 C%.*f\n",precision,priority[i].release);
               }
             else if(ctemp!=layer[entity[k].layer].zchar)
               {fprintf(ofp,"G00 %c%.*f\n",ctemp,precision,priority[i].release);
                ctemp=layer[entity[k].layer].zchar;
               }
             else fprintf(ofp,"G00 %c%.*f\n",layer[entity[k].layer].zchar,precision,priority[i].release);
             fprintf(ofp,"G00 X%.*f Y%.*f\n",precision,x2,precision,y2);
             fprintf(ofp,"G01 %c%.*f\n",layer[entity[k].layer].zchar,precision,z2);
            }
          if((dist1>.0001 && dist1<=priority[i].close) || fabs(z2-z1)>.0001)
            {fprintf(ofp,"G01 X%.*f Y%.*f %c%.*f\n",precision,x2,precision,y2,layer[entity[k].layer].zchar,precision,z2);
            }
          get_second_point(&x1, &y1, &z1, &entity[k]);
          //write entity
			 //Second point Z is optional here
          if(entity[k].type==LINE)
            {if(entity[k].dir==FOR)
               if (convertop.extraz==0) {
                 fprintf(ofp,"G01 X%.*f Y%.*f %c%.*f\n",precision,entity[k].x2,precision,entity[k].y2,
                       layer[entity[k].layer].zchar, precision,entity[k].z2);
                 }
               else {
                 fprintf(ofp,"G01 X%.*f Y%.*f\n",precision,entity[k].x2,precision,entity[k].y2);
                 }
             else
					if (convertop.extraz==0) {
                 fprintf(ofp,"G01 X%.*f Y%.*f %c%.*f\n",precision,entity[k].x1,precision,entity[k].y1,
                       layer[entity[k].layer].zchar, precision,entity[k].z1);
                 }
               else {
                 fprintf(ofp,"G01 X%.*f Y%.*f\n",precision,entity[k].x1,precision,entity[k].y1);
                 }
              }

          if(entity[k].type==ARC)
            {if(entity[k].dir==CCW)
               {if(convertop.ijfirst==1)
                  {if(convertop.ijrel==1)
                     fprintf(ofp,"G03 I%.*f J%.*f X%.*f Y%.*f\n",
                             precision,-entity[k].radius*cos(entity[k].ang_start),
                             precision,-entity[k].radius*sin(entity[k].ang_start),
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_end),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_end));
                   else
                     fprintf(ofp,"G03 I%.*f J%.*f X%.*f Y%.*f\n",
                             precision,entity[k].x1, precision,entity[k].y1,
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_end),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_end));
                  }
                else
                  {if(convertop.ijrel==1)
                     fprintf(ofp,"G03 X%.*f Y%.*f I%.*f J%.*f\n",
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_end),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_end),
                             precision,-entity[k].radius*cos(entity[k].ang_start),
                             precision,-entity[k].radius*sin(entity[k].ang_start));
                   else
                     fprintf(ofp,"G03 X%.*f Y%.*f I%.*f J%.*f\n",
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_end),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_end),
                             precision,entity[k].x1, precision,entity[k].y1);
                  }
               }
             else
               {if(convertop.ijfirst==1)
                  {if(convertop.ijrel==1)
                     fprintf(ofp,"G02 I%.*f J%.*f X%.*f Y%.*f\n",
                             precision,-entity[k].radius*cos(entity[k].ang_end),
                             precision,-entity[k].radius*sin(entity[k].ang_end),
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_start),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_start));
                  else
                     fprintf(ofp,"G02 I%.*f J%.*f X%.*f Y%.*f\n",
                             precision,entity[k].x1, precision,entity[k].y1,
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_start),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_start));
                  }
                else
                  {if(convertop.ijrel==1)
                     fprintf(ofp,"G02 X%.*f Y%.*f I%.*f J%.*f\n",
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_start),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_start),
                             precision,-entity[k].radius*cos(entity[k].ang_end),
                             precision,-entity[k].radius*sin(entity[k].ang_end));
                   else
                     fprintf(ofp,"G02 X%.*f Y%.*f I%.*f J%.*f\n",
                             precision,entity[k].x1+entity[k].radius*cos(entity[k].ang_start),
                             precision,entity[k].y1+entity[k].radius*sin(entity[k].ang_start),
                             precision,entity[k].x1, precision,entity[k].y1);
                  }
               }
            }
         }
      if(num_of_ent>0)
        {fprintf(ofp,"G00 %c%.*f\n",layer[entity[num_of_ent-1].layer].zchar,precision,priority[i].release);
        }
      //write postcode to file
      if(demo==0 || (demo==1 && count<=20))
        {fprintf(ofp,"%s",priority[i].postcode);
         if(strlen(priority[i].postcode)>0 &&
            priority[i].postcode[strlen(priority[i].postcode)-1]!='\n') fputc('\n',ofp);
        }
     }
   fclose(ofp);
   fclose(ifp);
   if(convertop.line_num==1)
     {ifp=fopen(szToFileName,"r");
      ofp=fopen("temp.tmp","w");
      while((ctemp=fgetc(ifp))!=EOF)
        {if(ctemp!='\n') {fprintf(ofp,"N%u ",10*line_num++); fputc(ctemp, ofp);}
         else {fputc(ctemp, ofp); continue;}
         while((ctemp=fgetc(ifp))!=EOF) {fputc(ctemp, ofp); if(ctemp=='\n') break;}
         if(ctemp==EOF) break;
        }
      fclose(ofp);
      fclose(ifp);
      ifp=fopen("temp.tmp","r");
      ofp=fopen(szToFileName,"w");
      while((ctemp=fgetc(ifp))!=EOF) fputc(ctemp, ofp);
      fclose(ifp);
      fclose(ofp);
      remove("temp.tmp");
     }
   if(demo==1)
     {ofp=fopen(szToFileName,"a");
      fprintf(ofp,"\n\nThank You For Evaluating ACEconverter\n");
      fprintf(ofp,"Converting Has Stopped Because Of The\n");
      fprintf(ofp,"Evaluation Limit.  To Order Your Licensed\n");
      fprintf(ofp,"Version Of ACEconverter Go To:\n");
      fprintf(ofp,"The World Wide Web At:\n");
      fprintf(ofp,"http://www.yeagerautomation.com\n");
      fclose(ofp);
     }
   sprintf(status,"Converting Complete");
   //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
   printf("%s",status );
   DONE:
   if(msg==1)
     {fclose(ofp);
      fclose(ifp);
      sprintf(status,"Invalid .dxf File Format");
      //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
      printf("%s",status );
     }
   if(msg==2)
     {fclose(ofp);
      fclose(ifp);
      sprintf(status,"Out Of Memory, Converting Aborted");
      //SetWindowText(GetDlgItem(hWindow, IDD_STATUS),status);
      printf("%s",status );
     }
   //farfree(entity);
   //EnableWindow(GetDlgItem(hWindow,IDD_CONVERT), TRUE);
   //EnableWindow(GetDlgItem(hWindow,IDD_OPEN), TRUE);
   //EnableWindow(GetDlgItem(hWindow,IDD_LAYER), TRUE);
   //EnableWindow(GetDlgItem(hWindow,IDD_PRIORITY), TRUE);
  // _endthread();
}

int get_values(FILE *ifp, struct entity_obj *ent)
{
   static char string[100];
   int temp, temp2, mode=1;
   fpos_t pos;

   ent->x1=ent->y1=ent->z1=ent->x2=ent->y2=ent->z2=ent->radius=ent->ang_start=ent->ang_end=0;
   while(1)
     {fgetpos(ifp, &pos);
      if((temp=fscanf(ifp,"%s",string))==EOF || temp==0) return 0;
      if(strcmp(string,"0")==0) {fsetpos(ifp, &pos); return mode;}
      else if(strcmp(string,"10")==0) {if((temp=fscanf(ifp,"%lf",&(ent->x1)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"20")==0) {if((temp=fscanf(ifp,"%lf",&(ent->y1)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"30")==0) {if((temp=fscanf(ifp,"%lf",&(ent->z1)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"11")==0) {if((temp=fscanf(ifp,"%lf",&(ent->x2)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"21")==0) {if((temp=fscanf(ifp,"%lf",&(ent->y2)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"31")==0) {if((temp=fscanf(ifp,"%lf",&(ent->z2)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"40")==0) {if((temp=fscanf(ifp,"%lf",&(ent->radius)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"42")==0) {if((temp=fscanf(ifp,"%lf",&(ent->radius)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"50")==0) {if((temp=fscanf(ifp,"%lf",&(ent->ang_start)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"51")==0) {if((temp=fscanf(ifp,"%lf",&(ent->ang_end)))==0 || temp==EOF) return 0;}
      else if(strcmp(string,"70")==0)
        {if((temp=fscanf(ifp,"%d",&temp2))==0 || temp==EOF) return 0;
         else if((temp2&1)==1) mode=2;
        }
      else if((temp=fscanf(ifp,"%s",string))==0 || temp==EOF) return 0;
     }
}

int get_string(FILE *ifp, const char *string_match, char *string_ret)
{
   static char string[100];
   int temp;
   fpos_t pos;

   while(1)
     {fgetpos(ifp, &pos);
      if((temp=fscanf(ifp,"%s",string))==EOF || temp==0) return 0;
      if(strcmp(string,"0")==0) {fsetpos(ifp,&pos); return 1;}
      if(strcmp(string,string_match)==0)
        {if((temp=fscanf(ifp,"%s",string_ret))==0 || temp==EOF) return 0; 
         return 1;
        }
      else if((temp=fscanf(ifp,"%s",string))==0 || temp==EOF) return 0;
     }
}

void make_arc(struct entity_obj *ent)
{
   double x_mid, y_mid, angle, x_start, y_start, x_end, y_end, chord, dist;
   x_mid=((*ent).x2-(*ent).x1)/2;
   y_mid=((*ent).y2-(*ent).y1)/2;
   x_start=(*ent).x1;
   y_start=(*ent).y1;
   x_end=(*ent).x2;
   y_end=(*ent).y2;
   angle=atan2(y_mid,x_mid);
   if((*ent).radius>0) angle=angle+PI/2;
   else angle=angle-PI/2;
   chord=2*sqrt(pow(x_mid,2)+pow(y_mid,2));
   dist=(*ent).radius-(pow(chord/2,2)+pow((*ent).radius,2))/(2*(*ent).radius);
   (*ent).x1=x_start+x_mid+dist*cos(angle);
   (*ent).y1=y_start+y_mid+dist*sin(angle);
   if((*ent).radius<0)
     {(*ent).ang_start=atan2(y_start-(*ent).y1,x_start-(*ent).x1);
      (*ent).ang_end=atan2(y_end-(*ent).y1,x_end-(*ent).x1);
     }
   else
     {(*ent).ang_end=atan2(y_start-(*ent).y1,x_start-(*ent).x1);
      (*ent).ang_start=atan2(y_end-(*ent).y1,x_end-(*ent).x1);
     }
   (*ent).radius=fabs((pow(chord/2,2)+pow((*ent).radius,2))/(2*(*ent).radius));
}

void get_first_point(double *x, double *y, double *z, struct entity_obj *entity)
{
   if(entity->type==LINE)
     {if(entity->dir==FOR) {*x=entity->x1; *y=entity->y1; *z=entity->z1;}
      else {*x=entity->x2; *y=entity->y2; *z=entity->z2;}
     }
   if(entity->type==ARC)
     {if(entity->dir==CW) {*x=entity->x1+entity->radius*cos(entity->ang_end);
                           *y=entity->y1+entity->radius*sin(entity->ang_end);
                           *z=entity->z1;}
      else {*x=entity->x1+entity->radius*cos(entity->ang_start);
            *y=entity->y1+entity->radius*sin(entity->ang_start);
            *z=entity->z1;}
     }
   if(entity->type==POINT) {*x=entity->x1; *y=entity->y1; *z=entity->z1;}
}

void get_second_point(double *x, double *y, double *z, struct entity_obj *entity)
{
   if(entity->type==LINE)
     {if(entity->dir==REV) {*x=entity->x1; *y=entity->y1; *z=entity->z1;}
      else {*x=entity->x2; *y=entity->y2; *z=entity->z2;}
     }
   if(entity->type==ARC)
     {if(entity->dir==CCW) {*x=entity->x1+entity->radius*cos(entity->ang_end);
                           *y=entity->y1+entity->radius*sin(entity->ang_end);
                           *z=entity->z1;}
      else {*x=entity->x1+entity->radius*cos(entity->ang_start);
            *y=entity->y1+entity->radius*sin(entity->ang_start);
            *z=entity->z1;}
     }
   if(entity->type==POINT) {*x=entity->x1; *y=entity->y1; *z=entity->z1;}
}
double min(double num1, double num2)
{
return (num1>num2)?num2:num1;
}

int DelPriority(int num, int count)
{
   int i;
   if(num>0 && num<=count) free(priority[num-1].precode);
   if(num>0 && num<=count) free(priority[num-1].postcode);
   for(i=num;i<count;i++) priority[i-1]=priority[i];
   if(count==1) free(priority);
   return count-1;
}

int NewPriority(int count)
{
   int i;
   temp_pri=(struct priority_obj *) calloc((count+1), sizeof(struct priority_obj));
   for(i=0;i<count;i++) temp_pri[i]=priority[i];
   if(count>0) free(priority);
   priority=temp_pri;
   priority[count].release=defaultreleaseplane;
   priority[count].close=defaultcloseenough;
   priority[count].optimize=defaultpriorityoptimization;
   priority[count].precode=(char *) calloc(1, sizeof(char));
   priority[count].postcode=(char *) calloc(1, sizeof(char));
   return count+1;
}

int ReadLayer (char *file)
{
   int i, count=0, temp;
   char string[100];
   fpos_t pos;
   FILE *ifp;
   ifp=fopen(file,"r");
   while(1)
     {if((temp=fscanf(ifp,"%s",string))!=EOF && temp!=0 && strcmp(string,"0")==0)
        {fgetpos(ifp, &pos);
         if((temp=fscanf(ifp,"%s",string))!=EOF && temp!=0 && strcmp(string,"LAYER")==0)
           {while(1)
              {if((temp=fscanf(ifp,"%s",string))==EOF || temp==0) break;
               if(strcmp(string,"0")==0) break;
               else if(strcmp(string,"2")==0)
                 {temp_lay=(struct layer_obj *) calloc(++count, sizeof(struct layer_obj));
                  for(i=0;i<count-1;i++) temp_lay[i]=layer[i];
                  if(count>1) free(layer);
                  layer=temp_lay;
                  temp=fscanf(ifp,"%s",layer[count-1].name);
                  break;
                 }
               else if((temp=fscanf(ifp,"%s",string))==EOF || temp==0) break;
              }
           }
         else fsetpos(ifp, &pos);
        }
      if(temp==0 || temp==EOF) break;
     }
   if(count==0)
     {layer=(struct layer_obj *) calloc(++count, sizeof(struct layer_obj));
      sprintf(layer[0].name,"0");
     }
   for(i=0;i<count;i++)
     {layer[i].status=1;
      layer[i].priority=1;
      layer[i].depth=defaultmaxzpass;
      layer[i].arc=IDD_EITHERARC;
      layer[i].zchar='Z';
      layer[i].zoffset=defaultzoffset;
     }
   fclose(ifp);
   return count;
}

void GetOption(char num, char dir[])
{
   int iTemp;
   static char szWinDir[50], szAceIni[50], szString[100];
   FILE *ifp;

   current_directory(szWinDir);
   sprintf(szAceIni,"%s\\ace.ini",szAcePath);
   if((ifp=fopen(szAceIni,"r"))!=NULL)
     {while((iTemp=fscanf(ifp,"%s",szString))!=EOF && strcmp(szString,"[1]")!=0);
      if(iTemp!=EOF)
        {iTemp=fgetc(ifp);
         while(1)
           {while(iTemp!=EOF && iTemp!='\n' && iTemp!='[') iTemp=fgetc(ifp);
            if(iTemp==EOF || iTemp=='[') break;
            iTemp=fgetc(ifp);
            if(iTemp==num && (iTemp=fgetc(ifp))=='=')
              {fgets(dir,50,ifp);
               iTemp=strlen(dir);
               if(iTemp>1) dir[iTemp-1]=0;
               if(iTemp>2 && dir[iTemp-2]=='\\') dir[iTemp-2]=0;
               break;
              }
           }
        }
      fclose(ifp);
     }
}

void SaveOption(char num, char dir[])
{
   int iTemp;
   static char szWinDir[50], szAceIni[50], szString[50];
   FILE *ifp, *ofp;

   current_directory(szWinDir);
   sprintf(szAceIni,"%s\\ace.ini",szAcePath);
   ofp=fopen("temp.tmp","w");
   if((ifp=fopen(szAceIni,"r"))!=NULL)
     {while(1)
        {if((iTemp=fgetc(ifp))=='[')
           {fputc(iTemp,ofp);
            if((iTemp=fgetc(ifp))=='1')
              {fputc(iTemp,ofp);
               if((iTemp=fgetc(ifp))==']')
                 {fputc(iTemp,ofp);
                  break;
                 }
              }
           }
         if(iTemp==EOF) break;
         fputc(iTemp, ofp);
        }
      if(iTemp!=EOF)
        {iTemp=fgetc(ifp);
         while(1)
           {while(iTemp!=EOF && iTemp!='\n') {fputc(iTemp,ofp); iTemp=fgetc(ifp);}
            if(iTemp==EOF) break;
            fputc(iTemp,ofp); iTemp=fgetc(ifp);
            if(iTemp==num)
              {fputc(iTemp,ofp); iTemp=fgetc(ifp);
               if(iTemp=='=')
                 {fputc(iTemp,ofp);
                  fgets(szString,50,ifp);
                  fprintf(ofp,"%s\n",dir);
                  iTemp=fgetc(ifp);
                 }
              }
           }
        }
      fclose(ifp);
     }
   fclose(ofp);
   ifp=fopen("temp.tmp","r");
   ofp=fopen(szAceIni,"w");
   while((iTemp=fgetc(ifp))!=EOF) fputc(iTemp, ofp);
   fclose(ifp);
   fclose(ofp);
   remove("temp.tmp");
}

char *current_directory(char *path)
{
  strcpy(path, "C:\\");      /* fill string with form of response: X:\ */
  //path[0] = 'A' + getdisk();   //Commented SD  /* replace X with current drive letter */
  //getcurdir(0, path+3); //Commented SD  /* fill rest of string with current directory */
  return(path);
}


