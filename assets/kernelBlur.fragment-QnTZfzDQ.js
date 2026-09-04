import{S as e}from"./QueenCombBabylon-BIAcetCj.js";import{k as i}from"./kernelBlurVaryingDeclaration-BhJ0qQ9d.js";import{p as s}from"./packingFunctions-BPe9MWqq.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-eC2XFed4.js";import"./index-CPCuwncr.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const t="kernelBlurFragment",o=`#ifdef DOF
factor=sampleCoC(sampleCoord{X}); 
computedWeight=KERNEL_WEIGHT{X}*factor;sumOfWeights+=computedWeight;
#else
computedWeight=KERNEL_WEIGHT{X};
#endif
#ifdef PACKEDFLOAT
blend+=unpack(texture2D(textureSampler,sampleCoord{X}))*computedWeight;
#else
blend+=texture2D(textureSampler,sampleCoord{X})*computedWeight;
#endif
`;e.IncludesShadersStore[t]||(e.IncludesShadersStore[t]=o);const f={name:t,shader:o},n="kernelBlurFragment2",a=`#ifdef DOF
factor=sampleCoC(sampleCenter+delta*KERNEL_DEP_OFFSET{X});computedWeight=KERNEL_DEP_WEIGHT{X}*factor;sumOfWeights+=computedWeight;
#else
computedWeight=KERNEL_DEP_WEIGHT{X};
#endif
#ifdef PACKEDFLOAT
blend+=unpack(texture2D(textureSampler,sampleCenter+delta*KERNEL_DEP_OFFSET{X}))*computedWeight;
#else
blend+=texture2D(textureSampler,sampleCenter+delta*KERNEL_DEP_OFFSET{X})*computedWeight;
#endif
`;e.IncludesShadersStore[n]||(e.IncludesShadersStore[n]=a);const m={name:n,shader:a},l="kernelBlurPixelShader",d=`uniform sampler2D textureSampler;uniform vec2 delta;varying vec2 sampleCenter;
#ifdef DOF
uniform sampler2D circleOfConfusionSampler;float sampleCoC(in vec2 offset) {float coc=texture2D(circleOfConfusionSampler,offset).r;return coc; }
#endif
#include<kernelBlurVaryingDeclaration>[0..varyingCount]
#ifdef PACKEDFLOAT
#include<packingFunctions>
#endif
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void)
{float computedWeight=0.0;
#ifdef PACKEDFLOAT
float blend=0.;
#else
vec4 blend=vec4(0.);
#endif
#ifdef DOF
float sumOfWeights=CENTER_WEIGHT; 
float factor=0.0;
#ifdef PACKEDFLOAT
blend+=unpack(texture2D(textureSampler,sampleCenter))*CENTER_WEIGHT;
#else
blend+=texture2D(textureSampler,sampleCenter)*CENTER_WEIGHT;
#endif
#endif
#include<kernelBlurFragment>[0..varyingCount]
#include<kernelBlurFragment2>[0..depCount]
#ifdef PACKEDFLOAT
gl_FragColor=pack(blend);
#else
gl_FragColor=blend;
#endif
#ifdef DOF
gl_FragColor/=sumOfWeights;
#endif
}`;e.ShadersStore[l]||(e.ShadersStore[l]=d);const u=[i,s,f,m];for(const r of u)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const O={name:l,shader:d};export{O as kernelBlurPixelShader};
