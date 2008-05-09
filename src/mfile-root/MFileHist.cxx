#include "MFileHist.h"

MFileHist::MFileHist()
{
	fHist = NULL;
	fInfo = NULL;
}

MFileHist::~MFileHist()
{
	delete fInfo;
	
	if(fHist)
		mclose(fHist);
}

int MFileHist::Open(char *fname)
{
    fHist = mopen(fname, "r");
    if(!fHist)
    	return kFailure;

	fInfo = new minfo;

    if( mgetinfo(fHist, fInfo) != 0 ) {
		delete fInfo;
		fInfo = NULL;
		
		mclose(fHist);
		fHist = NULL;
		        
        return kFailure;
    }
    
    return kSuccess;
}

int MFileHist::Close()
{
	int stat = kSuccess;

	delete fInfo;
	fInfo = NULL;
	
	if(fHist)
		stat = mclose(fHist);
	fHist = NULL;
	
	return stat;
}

template <class histType>
histType *MFileHist::ToTH1(char *name, char *title, int level, int line)
{
	histType *hist;

	if(!fHist || !fInfo)
		return NULL;
	if(level >= fInfo->levels || line >= fInfo->lines)
		return NULL;
		
	hist = new histType(name, title, fInfo->columns, -0.5, (double) fInfo->columns - 0.5);
	
	if(!FillTH1(hist, level, line)) {
		delete hist;
		return NULL;
	}
	
	return hist;
}

TH1 *MFileHist::FillTH1(TH1 *hist, int level, int line)
{
	if(!fHist || !fInfo)
		return NULL;
	if(level >= fInfo->levels || line >= fInfo->lines)
		return NULL;
		
	double *buf = new double[fInfo->columns];

    if(mgetdbl(fHist, buf, level, line, 0, fInfo->columns) != fInfo->columns) {
    	delete buf;
    	return NULL;
    }
    
	for(int i=0; i < fInfo->columns; i++) {
		hist->SetBinContent(i+1, buf[i]);
	}
	
	delete buf;
	
	return hist;
}

TH1D *MFileHist::ToTH1D(char *name, char *title, int level, int line)
{
	return ToTH1<TH1D>(name, title, level, line);
}

TH1I *MFileHist::ToTH1I(char *name, char *title, int level, int line)
{
	return ToTH1<TH1I>(name, title, level, line);
}
