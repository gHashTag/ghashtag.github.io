import{S as e}from"./QueenCombBabylon-Ch90MSLm.js";const d="instancesDeclaration",o=`#ifdef INSTANCES
attribute vec4 world0;attribute vec4 world1;attribute vec4 world2;attribute vec4 world3;
#ifdef INSTANCESCOLOR
attribute vec4 instanceColor;
#endif
#if defined(THIN_INSTANCES) && !defined(WORLD_UBO)
uniform mat4 world;
#endif
#if defined(VELOCITY) || defined(PREPASS_VELOCITY) || defined(PREPASS_VELOCITY_LINEAR) || defined(VELOCITY_LINEAR)
attribute vec4 previousWorld0;attribute vec4 previousWorld1;attribute vec4 previousWorld2;attribute vec4 previousWorld3;
#ifdef THIN_INSTANCES
uniform mat4 previousWorld;
#endif
#endif
#else
#if !defined(WORLD_UBO)
uniform mat4 world;
#endif
#if defined(VELOCITY) || defined(PREPASS_VELOCITY) || defined(PREPASS_VELOCITY_LINEAR) || defined(VELOCITY_LINEAR)
uniform mat4 previousWorld;
#endif
#endif
`;e.IncludesShadersStore[d]||(e.IncludesShadersStore[d]=o);const s={name:d,shader:o},i="fogVertex",n=`#ifdef FOG
vFogDistance=(view*worldPos).xyz;
#endif
`;e.IncludesShadersStore[i]||(e.IncludesShadersStore[i]=n);const a={name:i,shader:n},r="vertexColorMixing",t=`#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
vColor=vec4(1.0);
#ifdef VERTEXCOLOR
#ifdef VERTEXALPHA
vColor*=colorUpdated;
#else
vColor.rgb*=colorUpdated.rgb;
#endif
#endif
#ifdef INSTANCESCOLOR
vColor*=instanceColor;
#endif
#endif
`;e.IncludesShadersStore[r]||(e.IncludesShadersStore[r]=t);const S={name:r,shader:t};export{a as f,s as i,S as v};
