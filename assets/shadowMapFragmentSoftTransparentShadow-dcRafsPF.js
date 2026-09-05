import{bI as a}from"./Queen-Cw0Rpa4M.js";import"./index-DRQo-Ljl.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const r="shadowMapFragmentSoftTransparentShadow",o=`#if SM_SOFTTRANSPARENTSHADOW==1
if ((bayerDither8(floor(mod(gl_FragCoord.xy,8.0))))/64.0>=softTransparentShadowSM.x*alpha) discard;
#endif
`;a.IncludesShadersStore[r]||(a.IncludesShadersStore[r]=o);const n={name:r,shader:o};export{n as shadowMapFragmentSoftTransparentShadow};
