void VMatrix::AddRegion(list<int> reglist, int c1, int c2)
{
  list<int>::iterator iter, next;
  bool inside = false;
  int min, max;
  
  min = TMath::Min(c1, c2);
  max = TMath::Max(c1, c2);

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

TH1 *VMatrix::Cut()
{
  
}
