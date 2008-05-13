void VMatrix::AddRegion(list<int> reglist, int l1, int l2)
{
  list<int>::iterator iter, next;
  bool inside = false;
  int min, max;
  
  min = TMath::Min(l1, l2);
  max = TMath::Max(l1, l2);
  
  // Perform clipping
  if(max < 0 || min >= fMatrix->GetNColumns()) return;
  min = TMath::Max(min, 0);
  max = TMath::Min(max, fMatrix->GetNColumns() - 1);

  iter = reglist.begin();
  while(iter != reglist.end() && *iter < min) {
    inside = !inside;
    iter++;
  }
  
  if(!inside) {
    iter = reglist.insert(iter, min);
    iter++;
  }
  
  while(iter != reglist.end() && *iter < max) {
    inside = !inside;
    next = iter; next++;
    reglist.erase(iter);
    iter = next;
  }
  
  if(!inside) {
    reglist.insert(iter, max);
  }
}

TH1 *VMatrix::Cut(const char *histname, const char *histtitle)
{
  int l, l1, l2;   // lines
  int c, cols = fMatrix->GetNColumns();   // columns
  list<int>::iterator iter;
  int nCut=0, nBg=0;   // total number of cut and background lines
  
  // Temporary buffer
  double *buf = new double[cols];
  
  // Sum of cut lines
  double *sum = new double[cols];
  for(c=0; c<cols; c++) sum[c] = 0.0;
  
  // Sum of background lines
  double *bg = new double[cols];
  for(c=0; c<cols; c++) bg[c] = 0.0;
  
  try {
    // Add up all cut lines
    iter = fCutRegions.begin();
    while(*iter != fCutRegions.end()) {
      l1 = *iter++;
      l2 = *iter++;
      for(l=l1; l<=l2; l++) {
        if(!fMatrix->FillBuf1D(buf, fLevel, l))
          throw;

        for(c=0; c<cols; c++) {
           sum[c] += buf[c];
        }
      
        nCut++;
      }
      if(l<=l2) break;
    }
    if(*iter != fCutRegions.end()) {
       delete buf, sum, bg;
       return NULL;
    }
  
    // Add up all background lines
    iter = fBgRegions.begin();
    while(*iter != fBgRegions.end()) {
      l1 = *iter++;
      l2 = *iter++;
      for(l=l1; l<=l2; l++) {
        if(!fMatrix->FillBuf1D(buf, fLevel, l))
          throw;

        for(c=0; c<cols; c++) {
          bg[c] += buf[c];
        }
      
        nBg++;
      }
    }
    
    if(nCut <= 0) throw;
  
    double bgFac = nBg / nCut;
    hist = new TH1D(histname, histtitle, cols, -0.5, (double) cols - 0.5);
    for(c=0; c<cols; c++) {
      hist->SetBinContent(c+1, sum[c] - bg[c] * bgFac);
    }
  catch() {
    delete buf, sum, bg;
    delete hist;
    return NULL;
  }
  
  delete buf, sum, bg;

  return hist; 
}
