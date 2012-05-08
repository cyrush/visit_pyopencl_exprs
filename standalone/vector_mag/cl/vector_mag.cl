//
// vector_mag.cl
//

__kernel void  vector_mag(__global const float *u,
                          __global const float *v,
                          __global const float *w,
                          __global float *o)
{
     int gid = get_global_id(0);
     float4 uvw = (float4)(u[gid],v[gid],w[gid],1.0);
     uvw *= uvw;
     o[gid] = sqrt(uvw.x + uvw.y + uvw.z);
}
