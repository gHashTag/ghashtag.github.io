import{S as e}from"./QueenCombBabylon-Ccpv0aSp.js";import{f as s,a as l}from"./fogFragment-BL15YR4c.js";import{l as n}from"./logDepthDeclaration-Cv22Snx6.js";import{l as f}from"./logDepthFragment-CqsLegCp.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-kFVbQ4B_.js";import"./index-DjsccCAJ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const o="imageProcessingCompatibility",a=`#ifdef IMAGEPROCESSINGPOSTPROCESS
gl_FragColor.rgb=pow(gl_FragColor.rgb,vec3(2.2));
#endif
`;e.IncludesShadersStore[o]||(e.IncludesShadersStore[o]=a);const c={name:o,shader:a},i="spritesPixelShader",t=`#ifdef LOGARITHMICDEPTH
#extension GL_EXT_frag_depth : enable
#endif
uniform bool alphaTest;varying vec4 vColor;varying vec2 vUV;uniform sampler2D diffuseSampler;
#include<fogFragmentDeclaration>
#include<logDepthDeclaration>
#define CUSTOM_FRAGMENT_DEFINITIONS
#ifdef PIXEL_PERFECT
vec2 uvPixelPerfect(vec2 uv) {vec2 res=vec2(textureSize(diffuseSampler,0));uv=uv*res;vec2 seam=floor(uv+0.5);uv=seam+clamp((uv-seam)/fwidth(uv),-0.5,0.5);return uv/res;}
#endif
void main(void) {
#define CUSTOM_FRAGMENT_MAIN_BEGIN
#ifdef PIXEL_PERFECT
vec2 uv=uvPixelPerfect(vUV);
#else
vec2 uv=vUV;
#endif
vec4 color=texture2D(diffuseSampler,uv);float fAlphaTest=float(alphaTest);if (fAlphaTest != 0.)
{if (color.a<0.95)
discard;}
color*=vColor;
#include<logDepthFragment>
#include<fogFragment>
gl_FragColor=color;
#include<imageProcessingCompatibility>
#define CUSTOM_FRAGMENT_MAIN_END
}`;e.ShadersStore[i]||(e.ShadersStore[i]=t);const d=[s,n,f,l,c];for(const r of d)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const C={name:i,shader:t};export{C as spritesPixelShader};
