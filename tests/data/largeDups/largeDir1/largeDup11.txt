{***********************************************************

 Program :  OH TOPMO3
 Version :  1.1
 Released:  25 May 1993
 Author  :  Kirill Shirokov
              The Future Hackers Co.
 CoAuthor:  Dmitry Moskovich

  This program illustrates visual effect, when english
  combinations of characters looks like russian text.
  Original idea was researched by Viacheslav Slavinsky
  (Some years ago he wrote genius line: KACEKOB - TOPMO3).

  Copyright by The Future Hackers Co., 1993
  All rights reserved.

************************************************************}

program OH_TOPMO3;

uses
  CRT;

const
  MHOrO_TEKCTOB         = 15;
  nPOPEXA               = nil;

type
  A_KTO_EBO_3HAET       = (HO_KTO_TO_BEgb_3HAET, BCE_ETO_BECbMA_CTPAHHO);

  HyMEP                 = Byte;

  CTPOKA                = String[15];

  TEKCTuK               = record
                            OHA: CTPOKA;
                            TOPMO3: HyMEP;
                          end;

  TAM_ABTOMAT           = ^ABTOMAT;

  ABTOMAT               = object
                            MOE_X, MOE_Y: HyMEP;
                            TEKCTOB_BCEBO: HyMEP;
                            TEKCTbl: array[1..MHOrO_TEKCTOB] of TEKCTuK;
                            KAKOE: HyMEP;
                            TOPMO3uM: HyMEP;
                            XPEH_EMy: TAM_ABTOMAT;

                            constructor BOT_EBOHOE_MECTO(X, Y: HyMEP);
                            procedure BOH_ETOT_XPEH(KOMy_XPEH: TAM_ABTOMAT);
                            procedure ETO_CTPOKA(OHA_CAMA: CTPOKA;
                                                 EE_TOPMO3: HyMEP);
                            procedure BblBOg;
                          end;

  XMblPb                = object
                            HE_KACEKOB: A_KTO_EBO_3HAET;
                            KTO_TAM_CAMOE_TAKOE: TAM_ABTOMAT;

                            constructor Hy_HuKAK_MHE_EBO_HE_HA3BATb;
                            procedure B_nyTb;
                            procedure u_EBO_TO3E
(uMEHHO_ETO_MOXHATOE_OHO_CAMOE:
TAM_ABTOMAT);
                        end;


procedure BAM_TEMHO;
begin
  ClrScr;
end;


procedure TOPMO3HyTb(CKOKO: HyMEP);
begin
  Delay(CKOKO);
end;


procedure rge_EMy_KBACuTb(EBO_X, EBO_Y: HyMEP);
begin
  GoToXY(EBO_X, EBO_Y);
end;


function WyXEP: Boolean;
begin
  WyXEP := KeyPressed;
end;


constructor ABTOMAT.BOT_EBOHOE_MECTO(X, Y: HyMEP);
begin
  MOE_X           := X;
  MOE_Y           := Y;
  TEKCTOB_BCEBO   := 0;
  KAKOE           := 0;
  TOPMO3uM        := 0;
end;


procedure ABTOMAT.BOH_ETOT_XPEH(KOMy_XPEH: TAM_ABTOMAT);
begin
  XPEH_EMy := KOMy_XPEH;
end;


procedure ABTOMAT.ETO_CTPOKA(OHA_CAMA: CTPOKA; EE_TOPMO3: HyMEP);
begin
  if TEKCTOB_BCEBO < MHOrO_TEKCTOB then begin
    Inc(TEKCTOB_BCEBO);
    with TEKCTbl[TEKCTOB_BCEBO] do begin
      OHA    := OHA_CAMA;
      TOPMO3 := EE_TOPMO3;
    end;
  end;
end;


procedure ABTOMAT.BblBOg;
begin
  if TEKCTOB_BCEBO > 0 then begin
    if TOPMO3uM = 0 then begin
      Inc(KAKOE);
      if KAKOE > TEKCTOB_BCEBO then KAKOE := 1;
      rge_EMy_KBACuTb(MOE_X, MOE_Y);
      with TEKCTbl[KAKOE] do begin
         Write(OHA);
         TOPMO3uM := TOPMO3;
      end;
    end;
    Dec(TOPMO3uM);
  end;
end;


constructor XMblPb.Hy_HuKAK_MHE_EBO_HE_HA3BATb;
begin
  KTO_TAM_CAMOE_TAKOE := nPOPEXA;
  HE_KACEKOB := BCE_ETO_BECbMA_CTPAHHO;
end;


procedure XMblPb.u_EBO_TO3E(uMEHHO_ETO_MOXHATOE_OHO_CAMOE: TAM_ABTOMAT);
begin
  if KTO_TAM_CAMOE_TAKOE = nPOPEXA then begin
    KTO_TAM_CAMOE_TAKOE := uMEHHO_ETO_MOXHATOE_OHO_CAMOE;
    uMEHHO_ETO_MOXHATOE_OHO_CAMOE^.XPEH_EMy :=
        uMEHHO_ETO_MOXHATOE_OHO_CAMOE;
  end
  else begin
    uMEHHO_ETO_MOXHATOE_OHO_CAMOE^.XPEH_EMy :=
        KTO_TAM_CAMOE_TAKOE^.XPEH_EMy;
    KTO_TAM_CAMOE_TAKOE^.XPEH_EMy := uMEHHO_ETO_MOXHATOE_OHO_CAMOE;
  end;
end;


procedure XMblPb.B_nyTb;
var
  ETOT_PAXuT: TAM_ABTOMAT;

begin
  ETOT_PAXuT := KTO_TAM_CAMOE_TAKOE;

  while not WyXEP do
    with ETOT_PAXuT^ do begin
      BblBOg;
      ETOT_PAXuT := XPEH_EMy;
      rge_EMy_KBACuTb(1, 10);
      TOPMO3HyTb(10);
    end;
end;


procedure BAM_XOPOWO;
begin
  BAM_TEMHO;
  WriteLN('OH TOPMO3 v1.0  Copyright The Future Hackers, 1993');
  WriteLN('(c) Written by Kirill Shirokov and Dmitry Moskovich, May 93');
  WriteLN;
end;


var
  EBO_3EHKu,
  EBO_HOC,
  EBO_POT,
  EBO_XBOCT     : ABTOMAT;

  KACEKOB       : XMblPb;


begin
  with KACEKOB do begin
    Hy_HuKAK_MHE_EBO_HE_HA3BATb;
    with EBO_3EHKu do begin
      BOT_EBOHOE_MECTO(1, 1);
      ETO_CTPOKA('-  -', 20);
      ETO_CTPOKA('o  o', 3);
      ETO_CTPOKA('O  O', 16);
      ETO_CTPOKA('0  0', 23);
      ETO_CTPOKA('O  O', 14);
      ETO_CTPOKA('o  o', 5);
    end;
    u_EBO_TO3E(@EBO_3EHKu);

    with EBO_HOC do begin
      BOT_EBOHOE_MECTO(1, 2);
      ETO_CTPOKA(' .. ', 21);
      ETO_CTPOKA(' oo ', 16);
    end;
    u_EBO_TO3E(@EBO_HOC);

    with EBO_POT do begin
      BOT_EBOHOE_MECTO(1, 3);
      ETO_CTPOKA(' -- ', 22);
      ETO_CTPOKA(' == ', 4);
      ETO_CTPOKA('-==-', 6);
      ETO_CTPOKA('/--', 19);
      ETO_CTPOKA('----', 16);
      ETO_CTPOKA(' ==/', 21);
      ETO_CTPOKA('----', 3);
    end;
    u_EBO_TO3E(@EBO_POT);

    BAM_TEMHO;
    B_nyTb;
    BAM_XOPOWO;
  end;
end.

{***********************************************************}
