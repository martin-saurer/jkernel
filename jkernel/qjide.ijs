NB. ****************************************************************************
NB. File:        qjide.ijs
NB. Author:      Martin Saurer, 18.02.2016
NB. Description: qjide J utilities.
NB.
NB. License:     GPL Version 3 (see gpl3.txt)
NB. ****************************************************************************

NB. ****************************************************************************
NB. Class definition
NB. We define our own locale for qjide.
NB. ****************************************************************************
coclass 'qjide'

NB. ****************************************************************************
NB. Extend output buffer
NB. ****************************************************************************
NB. 9!:37 (0,16384,0,16000)

NB. ****************************************************************************
NB. Setup box drawing characters
NB. ****************************************************************************
9!:7 (0{Boxes_j_)

NB. ****************************************************************************
NB. Load convert/json
NB. This add-on is used for data-exchange between J and the web stuff.
NB. ****************************************************************************
load 'convert/json'

NB. Here, we patch the JSONASC variable to include 8bit characters
JSONASC_json_ =: JSONESC0_json_, 32}.255{.a.

NB. ****************************************************************************
NB. Load ide/jhs
NB. This add-on is used for plotting to html canvas.
NB. ****************************************************************************
IFJHS_z_ =: 1
canvasnum_jhs_ =: 1
load 'jhs'

NB. ****************************************************************************
NB. To identify qjide is running, we define IFQJIDE
NB. ****************************************************************************
IFQJIDE_z_ =: 1

NB. ****************************************************************************
NB. Define a simple verb to load a file into editor from the command line
NB. ****************************************************************************
edit_z_ =: 3 : 0
   smoutput '$$$edit$$$',jpath y
)

NB. ****************************************************************************
NB. Load labs/labs
NB. This add-on is used to run J's great tutorials, called labs.
NB. ****************************************************************************
load '~addons/labs/labs/lab.ijs'

NB. Used by viewmat labs
smselout_jijs_ =: ]
smfocus_jijs_ =: ]
smact_z_ =: ]

NB. Get available labs
getlabs =: 3 : 0
   LABTITLES=: LABCATS=: LABFILES=: ''
   d=. dirpath t=. jpath'~addons/labs/labs'
   try.
      for_p. d do.
         for_q. 1 dir '/*.ijt',~>p do.
            LABFILES=: LABFILES,q
            cat=. (>:#t)}.>q
            cat=. (cat i.'/'){.cat
            LABCATS=:  LABCATS,<cat
            title=. toJ fread q
            title=. (title i.LF){.title
            title=. (>:title i.'''')}.title
            title=. (title i:''''){.title 
            LABTITLES=: LABTITLES,<cat,': ',title
         end.
      end.
   catch.
   end.
   s=. /:LABTITLES
   LABFILES=:  s{LABFILES
   LABCATS=:   s{LABCATS
   LABTITLES=: s{LABTITLES
)

NB. ****************************************************************************
NB. Load and init pacman (package manager)
NB. The pacman is part of the base system.
NB. Initialization after loading is necessary in J701 only, so we check whether
NB. the verb 'readconfig' is available in the _jpacman_ locale, and run it, if
NB. it exists.
NB. ****************************************************************************
load 'pacman'
pminit =: 3 : 0
   if. (+/(<'readconfig') E. nl_jpacman_'') > 0 do.
      tmpobj =: readconfig_jpacman_''
      tmpobj =: setfiles_jpacman_''
      tmpobj =: readlocal_jpacman_''
   end.
)
pminit''

NB. ****************************************************************************
NB. The Web Window Driver (wwd)
NB. ****************************************************************************

NB. Web window driver data (used by wwd*)
wwdsend_qjide_ =: ''
wwdinfo_qjide_ =: ''

NB. Define wwd verb
wwd =: 3 : 0
   NB. Get arguments
   if. (#y) = 2 do.
      cmd0 =. >0{y
      dat0 =. >1{y
   else.
      cmd0 =. y
      dat0 =. ''
   end.
   NB. Cut command part into its components
   cmd1 =. cut cmd0
   NB. Prepare data part for json encoding
   if. ($$dat0) = 2 do.
      dat1 =. <<"1 dat0
   else.
      dat1 =. <dat0
   end.
   NB. Glue command and data together
   cmda =. cmd1;dat1
   NB. Encode stuff as json string
   json =. enc_json cmda
   NB. Prepare wwdsend_qjide_
   wwdsend_qjide_ =: '[',json,']'
   NB. Dummy output
   smoutput ''
)

NB. Define wwdbeg verb
wwdbeg =: 3 : 0
   wwdsend_qjide_ =: ''
)

NB. Define wwdadd verb
wwdadd =: 3 : 0
   NB. Get arguments
   if. (#y) = 2 do.
      cmd0 =. >0{y
      dat0 =. >1{y
   else.
      cmd0 =. y
      dat0 =. ''
   end.
   NB. Cut command part into its components
   cmd1 =. cut cmd0
   NB. Prepare data part for json encoding
   if. ($$dat0) = 2 do.
      dat1 =. <<"1 dat0
   else.
      dat1 =. <dat0
   end.
   NB. Glue command and data together
   cmda =. cmd1;dat1
   NB. Encode stuff as json string
   json =. enc_json cmda
   NB. Add to wwdsend_qjide_
   if. (#wwdsend_qjide_) > 0 do.
      wwdsend_qjide_ =: wwdsend_qjide_,','
   end.
   wwdsend_qjide_ =: wwdsend_qjide_,json
)

NB. Define wwdend verb
wwdend =: 3 : 0
   wwdsend_qjide_ =: '[',wwdsend_qjide_,']'
   NB. Dummy output
   smoutput ''
)

NB. Define wwdget verb
wwdget =: 4 : 0
   if. $I.(<x)E.0{wwdinfo_qjide_ do.
      dat =. 0{>(I.(<x)E.0{wwdinfo_qjide_){1{wwdinfo_qjide_
   else.
      dat =. ''
   end.
   if. (#dat) > 0 do.
      if. (#y) > 0 do.
         if. $I.(<y)E.0{dat do.
            ret =. 0{>(I.(<y)E.0{dat){1{dat
         else.
            ret =. ''
         end.
      else.
         ret =. dat
      end.
   else.
      ret =. ''
   end.
)

NB. Define some verbs in z locale
wwd_z_    =: wwd_qjide_
wwdbeg_z_ =: wwdbeg_qjide_
wwdadd_z_ =: wwdadd_qjide_
wwdend_z_ =: wwdend_qjide_
wwdget_z_ =: wwdget_qjide_

NB. ****************************************************************************
NB. qjide in Qt/WebView
NB. ****************************************************************************

NB. Simple browser using Qt/WebView
qtqjide =: 3 : 0
   wd 'pc qtqjide'
   wd 'pn J Browser IDE'
   wd 'cc wv webview'
   wd 'pas 0 0'
   wd 'pshow'
   wd 'set wv url *http://127.0.0.1:8080'
)

qtqjide_close =: 3 : 0
   wd 'pclose'
)

NB. ****************************************************************************
NB. EOF
NB. ****************************************************************************
