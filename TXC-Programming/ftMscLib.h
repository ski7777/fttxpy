//=============================================================================
//              |
// Headerfile   |  ftMscLib.h
//              |
// Description  |  Function prototypes of Library ftMscLib
//              |
//-----------------------------------------------------------------------------
// Disclaimer - Exclusion of Liability
//
// This software is distributed in the hope that it will be useful,but WITHOUT 
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
// FITNESS FOR A PARTICULAR PURPOSE. It can be used an modified by anyone
// free of any license obligations or authoring rights.
//=============================================================================

#ifndef __FTMSCLIB_H__
#define __FTMSCLIB_H__


#ifndef  __cplusplus
	typedef BOOL bool;
#endif


#if defined(_DLL_VER)
#define DLLImp extern "C" __declspec(dllimport)
#else
#define DLLImp
#endif


//  port restriction COM ports
enum PortSelect {
    ALL_PORTS = 0,
    USB_ONLY,
    BT_ONLY
};


//  Transfer Area running status
//      0 - Transfer Area is not running
//      1 - Transfer Area is running
//      2 - Transfer Area is being synchronized
#define TA_STATUS_STOP      0
#define TA_STATUS_RUN       1
#define TA_STATUS_SYNC      2

//  status of I/O communication
//     0 - Remote I/O Request was sent
//     1 - Set Configuration Request was sent
#define SE_REMIO_REQ        0
#define SE_CONFIG_REQ       1

//  multi-controller-mode status (slave)
#define SLAVE_OFFLINE       0
#define SLAVE_ONLINE        1



// ============================================================================
//  TransferArea of all ROBO TX Controllers (Master + 8 Slaves)
//-----------------------------------------------------------------------------


//  Transfer Area of ftMscLib (Master TXC, 8 Slave TXC) 
typedef struct {

	TA	ftxTransferArea[TA_COUNT];

} TA_ARRAY;



//  ftMscLib function prototypes
//-----------------------------------------------------------------------------
DLLImp DWORD  ftxGetLibVersion(void);
DLLImp DWORD  ftxGetLibVersionStr(LPSTR, DWORD);
DLLImp DWORD  ftxInitLib(void);
DLLImp DWORD  ftxCloseLib(void);
DLLImp DWORD  ftxIsLibInit(void);
DLLImp DWORD  ftxGetSerialNrStrg (HANDLE, LPSTR, DWORD);
DLLImp DWORD  ftxGetFirmwareStrg(HANDLE, LPSTR, DWORD);
DLLImp DWORD  ftxGetManufacturerStrg(HANDLE, LPSTR, DWORD);
DLLImp DWORD  ftxGetShortNameStrg(HANDLE, LPSTR, DWORD);
DLLImp DWORD  ftxGetLongNameStrg(HANDLE, LPSTR, DWORD);
DLLImp DWORD  ftxGetLibErrorString(DWORD, DWORD, LPSTR, DWORD);

//  open, close connection to ROBO interface
DLLImp HANDLE ftxOpenComDevice(char *, DWORD, DWORD *);
DLLImp HANDLE ftxOpenComDeviceNr(DWORD, DWORD, DWORD *);
DLLImp DWORD  ftxCloseDevice(HANDLE);
DLLImp DWORD  ftxCloseAllDevices(void);

//  start, stop, status TransferArea
DLLImp DWORD  ftxStartTransferArea(HANDLE);
DLLImp DWORD  ftxStopTransferArea(HANDLE);
DLLImp DWORD  ftxIsTransferActiv(HANDLE);

//  get ftX1 Transfer address
DLLImp volatile TA_ARRAY   *GetTransferAreasArrayAddr(HANDLE);
DLLImp TA_STATUS           *GetTransferAreaStatusAddr(HANDLE, int);

//  communication status and info
DLLImp DWORD  ftxIsHandleValid(HANDLE);
DLLImp DWORD  GetComStatus(HANDLE);
DLLImp DWORD  GetAvailableComPorts(int);
DLLImp DWORD  EnumComPorts(DWORD, LPSTR, DWORD);

//  set fish.X1 output structure
DLLImp DWORD  StartCounterReset(HANDLE, int, int);
DLLImp void   SetCBCounterResetted(void (__stdcall *)(DWORD, DWORD));
DLLImp DWORD  SetOutMotorValues(HANDLE, int, int, int, int);
DLLImp DWORD  SetOutPwmValues(HANDLE, int, int, int);
DLLImp DWORD  StartMotorExCmd(HANDLE, int, int, int, int, int, int, int);
DLLImp DWORD  StopAllMotorExCmd(HANDLE, int);
DLLImp DWORD  StopMotorExCmd(HANDLE, int, int);
DLLImp void   SetCBMotorExReached(void (__stdcall *)(DWORD, DWORD));

DLLImp DWORD  SetRoboTxDevName(HANDLE, int, LPSTR);
DLLImp DWORD  SetRoboTxMessage(HANDLE, int, LPCSTR);

//  set fish.X1 config structure
DLLImp DWORD  SetFtUniConfig (HANDLE, int, int, int, bool);
DLLImp DWORD  SetFtCntConfig (HANDLE, int, int, int);
DLLImp DWORD  SetFtMotorConfig (HANDLE, int, int, bool);

//  get values from fish.X1 TransferArea, input structure
DLLImp DWORD  GetInIOValue(HANDLE, int, int, INT16 *, BOOL32 *);
DLLImp DWORD  GetInCounterValue (HANDLE, int, int, INT16 *, INT16 *);
DLLImp DWORD  GetInDisplayButtonValue (HANDLE, int, INT16 *, INT16 *);

//  file upload and remote commands to Robo08 Interface
DLLImp DWORD  FtRemoteCmd(HANDLE, char *, void (__stdcall *)(LPSTR, DWORD));
DLLImp DWORD  FtFileUpload(HANDLE, char *, DWORD, void (__stdcall *)(DWORD));
DLLImp DWORD  FtRamFileUpload(HANDLE, DWORD, CONST PVOID, DWORD, LPCSTR, void (__stdcall *)(DWORD));
DLLImp DWORD  RTxCleanDisk(HANDLE, DWORD);

//  set local program status
DLLImp DWORD  FtProgramRun(HANDLE, int);
DLLImp DWORD  FtProgramStop(HANDLE, int);

//  for Multi-Interface-Mode
DLLImp DWORD  GetRoboTxInfo(HANDLE, int);
DLLImp DWORD  GetRoboTxMasterState(HANDLE);
DLLImp DWORD  GetRoboTxSlaveState(HANDLE, BYTE *);
DLLImp DWORD  GetRoboTxSlaveAlive(HANDLE, int, BOOL *);
DLLImp DWORD  GetRoboTxBtStatus(HANDLE, BT_STATUS *);

//  fish.X1 info structure
DLLImp DWORD  GetRoboTxDevName(HANDLE, int, LPSTR, DWORD);
DLLImp DWORD  GetRoboTxBtAddr(HANDLE, int, LPSTR, DWORD);
DLLImp DWORD  GetRoboTxFwStr(HANDLE, int, LPSTR, DWORD);
DLLImp DWORD  GetRoboTxFwVal(HANDLE, int, DWORD *);
DLLImp DWORD  GetRoboTxHwStr(HANDLE, int, LPSTR, DWORD);
DLLImp DWORD  GetRoboTxMemLayout(HANDLE, int, PULONG, PULONG, PULONG);
DLLImp DWORD  GetRoboTxSerialStr(HANDLE, int, LPSTR, DWORD);
DLLImp DWORD  GetRoboTxDllStr(HANDLE, int, LPSTR, DWORD);

//  set callback function for Multi-Interface-Mode status
DLLImp void   SetCBRoboExtState(void (__stdcall *)(DWORD, DWORD));

//  get transfer statistics, info
DLLImp DWORD  GetSessionId(void);
DLLImp DWORD  GetTrapStatistic(HANDLE, DWORD *, DWORD *, DWORD *, DWORD *, DWORD *, DWORD *);
DLLImp void   ResetTrapStatistic(HANDLE);

//  firmware update
DLLImp DWORD  RoboTxFwUpdate(HANDLE, LPCSTR, void (__stdcall *)(DWORD, LPSTR));

//  bluetooth management api
DLLImp DWORD  StartScanBtDevice(HANDLE, void (__stdcall *)(BT_SCAN_STATUS *));
DLLImp DWORD  CancelScanBtDevice(HANDLE);
DLLImp DWORD  ConnectBtAddress(HANDLE, DWORD, BYTE *, void (__stdcall *) (BT_CB *));
DLLImp DWORD  DisconnectBt(HANDLE, DWORD, void (__stdcall *) (BT_CB *));
DLLImp DWORD  SendBtMessage(HANDLE, DWORD, DWORD, LPSTR, void (__stdcall *) (BT_CB *));
DLLImp DWORD  BtListenConOn(HANDLE, DWORD, BYTE *, void (__stdcall *) (BT_CB *));
DLLImp DWORD  BtListenConOff(HANDLE, DWORD, void (__stdcall *) (BT_CB *));
DLLImp DWORD  BtReadMsgOn(HANDLE, DWORD, void (__stdcall *) (BT_RECV_CB *));
DLLImp DWORD  BtReadMsgOff(HANDLE, DWORD, void (__stdcall *) (BT_CB *));
DLLImp void   StatusBtConnection(DWORD, BT_STATUS *);

//  i2c management api
DLLImp DWORD  ftxI2cRead(HANDLE, BYTE, DWORD, BYTE, void (__stdcall *)(I2C_CB *));
DLLImp DWORD  ftxI2cWrite(HANDLE, BYTE, DWORD, WORD, BYTE, void (__stdcall *)(I2C_CB *));


#endif
