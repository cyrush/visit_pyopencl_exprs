//
// vorticity_3d.cl
//

__kernel void  vorticity_3d(__constant const int *d,
                            __global const float *x,
                            __global const float *y,
                            __global const float *z,
                            __global const float *u, 
                            __global const float *v, 
                            __global const float *w,
                            __global float *o)
{
     int gid = get_global_id(0);

     int di = d[0]-1;
     int dj = d[1]-1;
     int dk = d[2]-1;

     int zi = gid % di;
     int zj = (gid / di) % dj;
     int zk = (gid / di) / dj;

     // for rectilinear, we only need 2 points to get dx,dy,dz
     int pi0 = zi + zj*(di+1) + zk*(di+1)*(dj+1);
     int pi1 = zi + 1 + (zj+1)*(di+1) + (zk+1)*(di+1)*(dj+1);

     float4 uvw = (float4)(u[gid],v[gid],w[gid],1.0);
     float4 p_0 = (float4)(x[pi0],y[pi0],z[pi0],1.0);
     float4 p_1 = (float4)(x[pi1],y[pi1],z[pi1],1.0);
     float4 dg  = p_1 - p_0;
     
     // x component
     float4 u_0 = (float4)(uvw.x,uvw.x,uvw.x,1.0);
     float4 u_1 = (float4)(uvw.x,uvw.x,uvw.x,1.0);

     // y component
     float4 v_0 = (float4)(uvw.y,uvw.y,uvw.y,1.0);
     float4 v_1 = (float4)(uvw.y,uvw.y,uvw.y,1.0);

     // z component
     float4 w_0 = (float4)(uvw.z,uvw.z,uvw.z,1.0);
     float4 w_1 = (float4)(uvw.z,uvw.z,uvw.z,1.0);

     // i bounds
     if(zi > 0)
     {
         u_0.x = u[gid-1];
         v_0.x = v[gid-1];
         w_0.x = w[gid-1];
     }
     
     if(zi < (di-1))
     {
         u_1.x = u[gid+1];
         v_1.x = v[gid+1];
         w_1.x = w[gid+1];
     }

     // j bounds   
     if(zj > 0)
     {
         u_0.y = u[gid-di];
         v_0.y = v[gid-di];
         w_0.y = w[gid-di];
     }
     if(zj < (dj-1))
     {
         u_1.y = u[gid+di];
         v_1.y = v[gid+di];
         w_1.y = w[gid+di];         
     }
     
     // k bounds
     if(zk > 0)
     {
        u_0.z = u[gid-(di*dj)];
        v_0.z = v[gid-(di*dj)];
        w_0.z = w[gid-(di*dj)];
     }
     
     if(zk < (dk-1))
     {
         u_1.z = u[gid+(di*dj)];
         v_1.z = v[gid+(di*dj)];
         w_1.z = w[gid+(di*dj)];
     }
   
     float4 du = (u_1 - u_0) / dg;
     float4 dv = (v_1 - v_0) / dg;
     float4 dw = (w_1 - w_0) / dg;
     // central diff if we aren't on the edges
     if( (zi != 0) && (zi != (di-1)))
     {
         du.x *= .5;
         dv.x *= .5;
         dw.x *= .5;
     }
     
     // central diff if we aren't on the edges
     if( (zj != 0) && (zj != (dj-1)))
     {
         du.y *= .5;
         dv.y *= .5;
         dw.y *= .5;
     }

     // central diff if we aren't on the edges
     if( (zk != 0) && (zk != (dk-1)))
     {    
         du.z *= .5;
         dv.z *= .5;
         dw.z *= .5;
     }

     float4 vort = (float4) (dw.y - dv.z,du.z - dw.x,dv.x - du.y,0.0);
     vort *= vort;
     o[gid] = sqrt(vort.x + vort.y + vort.z);
     //o[gid*3]   = dw.y - dv.z;
     //o[gid*3+1] = du.z - dw.x;
     //o[gid*3+2] = dv.x - du.y;
}
