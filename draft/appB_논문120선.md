# 부록 B. 주요 논문 50선 (테마별 핵심)

> 이 목록은 모든 논문을 다 읽으라는 숙제가 아닙니다. 각 테마의 **핵심 3~7편** 만 엄선해 남겼습니다. 더 깊게 들어가고 싶다면 저자 GitHub 의 확장 리딩 리스트를 참고해 주세요.
> 확장 리스트: https://github.com/leelang7/physical-ai-book/blob/main/docs/reading-list.md (출간 시 공개)

---

## B.1 비전 기초 (1~8장)

1. Krizhevsky et al., **ImageNet Classification with Deep CNNs** (NIPS 2012) — AlexNet
2. He et al., **Deep Residual Learning** (CVPR 2016) — ResNet
3. Dosovitskiy et al., **An Image is Worth 16×16 Words** (ICLR 2021) — ViT
4. Radosavovic et al., **Designing Network Design Spaces** (CVPR 2020) — RegNet
5. Tan et al., **EfficientDet (BiFPN)** (CVPR 2020)
6. Wang et al., **YOLOv10** (NeurIPS 2024)
7. He et al., **MAE: Masked Autoencoders Are Scalable Vision Learners** (CVPR 2022)
8. Oquab et al., **DINOv2** (arXiv 2023)

## B.2 자율주행 인식 (4~8장)

9. Philion & Fidler, **Lift, Splat, Shoot** (ECCV 2020)
10. Li et al., **BEVFormer** (ECCV 2022)
11. Wang et al., **StreamPETR** (ICCV 2023)
12. Wei et al., **SurroundOcc** (ICCV 2023)
13. Tong et al., **UniAD** (CVPR 2023 Best Paper) — E2E 통합
14. Carion et al., **DETR** (ECCV 2020)
15. Zhao et al., **RT-DETR** (CVPR 2024)
16. Zheng et al., **CLRNet** (CVPR 2022)

## B.3 End-to-End 자율주행 (3, 10장)

17. Bojarski et al., **End to End Learning for Self-Driving Cars** (arXiv 2016) — NVIDIA E2E 시초
18. Hu et al., **GAIA-1** (arXiv 2023) — Wayve 월드 모델
19. Wang et al., **DriveWorld** (CVPR 2024)

## B.4 예측 (9장)

20. Gao et al., **VectorNet** (CVPR 2020)
21. Varadarajan et al., **MultiPath++** (ICRA 2022)
22. Ngiam et al., **Scene Transformer** (ICLR 2022)
23. Shi et al., **MTR** (NeurIPS 2022)

## B.5 데이터 엔진 · 시뮬레이션 (12~14장)

24. Dosovitskiy et al., **CARLA** (CoRL 2017)
25. Caesar et al., **nuScenes** (CVPR 2020)
26. Sun et al., **Waymo Open Dataset** (CVPR 2020)
27. Yu et al., **BDD100K** (CVPR 2020)
28. Gulino et al., **Waymax** (NeurIPS 2023)

## B.6 분산 학습 · MLOps (15~17장)

29. Rajbhandari et al., **ZeRO** (SC 2020)
30. Dao et al., **FlashAttention** (NeurIPS 2022)
31. Dao, **FlashAttention-2** (2023) · Shah et al., **FlashAttention-3** (2024)
32. Hinton et al., **Distilling the Knowledge in a Neural Network** (arXiv 2015)
33. Frantar et al., **GPTQ** (ICLR 2023)

## B.7 Physical AI · 로봇학습 (18~22장)

34. Ha & Schmidhuber, **World Models** (NIPS 2018)
35. Hafner et al., **DreamerV3** (Nature 2025)
36. Brohan et al., **RT-2** (CoRL 2023)
37. Kim et al., **OpenVLA** (CoRL 2024)
38. NVIDIA, **GR00T N1** (tech report 2025)
39. Google DeepMind, **Gemini Robotics** (2025)
40. Chi et al., **Diffusion Policy** (RSS 2023)
41. Zhao et al., **ALOHA** (RSS 2023)
42. Fu et al., **Mobile ALOHA** (arXiv 2024)
43. Team Open-X, **Open X-Embodiment** (ICRA 2024)

## B.8 모방학습 · 강화학습 (20~21장)

44. Ross, Gordon, Bagnell, **A Reduction of Imitation Learning... (DAgger)** (AISTATS 2011)
45. Kelly et al., **HG-DAgger** (ICRA 2019)
46. Schulman et al., **PPO** (arXiv 2017)
47. Kumar et al., **RMA** (RSS 2021)
48. Rudin et al., **ANYmal Parkour** (Science Robotics 2024)
49. Peng et al., **AMP** (SIGGRAPH 2021)
50. Rafailov et al., **DPO** (NeurIPS 2023)

---

## 독자용 TOP 10 — 꼭 읽어 보세요

입문자라면 **이 10편** 부터 시작하세요. 나머지는 필요해질 때 한 편씩 보시면 됩니다.

1 · AlexNet · **2 · ResNet** · **9 · Lift-Splat-Shoot** · **10 · BEVFormer** · **13 · UniAD** · **21 · MultiPath++** · **30 · FlashAttention** · **34 · World Models** · **36 · RT-2** · **44 · DAgger**

---

## 논문 읽는 법 — 짧은 팁

- **Abstract → Figure 1 → Table 1 → Conclusion** 순서로 5분 이내에 파악
- 흥미로우면 Method 섹션으로
- 구현하고 싶으면 Appendix + 저자 GitHub
- 한 번에 한 편. "페이퍼 다이어리" 를 권장합니다.
