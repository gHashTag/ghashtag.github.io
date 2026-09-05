import{bM as e}from"./Queen-CMaJNJEY.js";import{f as s,a as l}from"./fogFragment-DOKrORMa.js";import{l as n}from"./logDepthDeclaration-DAavlat9.js";import{l as f}from"./logDepthFragment-D1oMN5FV.js";import"./index-BLhDdMEg.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const o="imageProcessingCompatibility",i=`#ifdef IMAGEPROCESSINGPOSTPROCESS
gl_FragColor.rgb=pow(gl_FragColor.rgb,vec3(2.2));
#endif
`;e.IncludesShadersStore[o]||(e.IncludesShadersStore[o]=i);const c={name:o,shader:i},a="spritesPixelShader",t=`#ifdef LOGARITHMICDEPTH
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
}`;e.ShadersStore[a]||(e.ShadersStore[a]=t);const d=[s,n,f,l,c];for(const r of d)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const P={name:a,shader:t};export{P as spritesPixelShader};
