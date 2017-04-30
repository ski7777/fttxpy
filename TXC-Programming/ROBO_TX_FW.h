//=============================================================================
// Header file with definition of the software interface to the
// ROBO TX Controller firmware.
// Can be used for building C-programs which can run under control
// of the ROBO TX Controller firmware in download (local) mode or
// for building PC-programs which can communicate with the
// ROBO TX Controller firmware in online mode.
//
// Disclaimer - Exclusion of Liability
//
// This software is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. It can be used and modified by anyone
// free of any license obligations or authoring rights.
//=============================================================================

#ifndef __ROBO_TX_FW_H__
#define __ROBO_TX_FW_H__


#define N_CNT                   4           // Number of counters
#define N_PWM_CHAN              8           // Number of PWM channels
#define N_MOTOR                 4           // Number of motors
#define N_UNI                   8           // Number of universal inputs

// 5kOhm range
#define R_MIN                   10          // [Ohm]
#define R_MAX                   4999        // [Ohm]
#define R_OVR                   5000        // [Ohm] overload

// 10V range
#define U_MIN                   0           // [mV]
#define U_MAX                   9999        // [mV]
#define U_OVR                   10000       // [mV] overload

// Ultrasonic Sensor range
#define ULTRASONIC_MIN          2           // [cm]
#define ULTRASONIC_MAX          1023        // [cm]
#define ULTRASONIC_OVR          1024        // [cm] overload
#define NO_ULTRASONIC           4096        // Not present

// Motor outputs PWM values range
#define DUTY_MIN                0
#define DUTY_MAX                512

// Length of strings
#define DEV_NAME_LEN_MAX        16          // "ROBO TX-xxxxxxxx"
#define BT_ADDR_STR_LEN         17          // "xx:xx:xx:xx:xx:xx"
#define DISPL_MSG_LEN_MAX       98          // Max. length of a pop-up display message

// Number of Bluetooth channels
#define BT_CNT_MAX              8

// Allowed values for channel index are 1...8
#define BT_CHAN_IDX_MIN         1
#define BT_CHAN_IDX_MAX         8

#define BT_ADDR_LEN             6           // Bluetooth address length
#define BT_MSG_LEN              16          // Max. Bluetooth message length


// Bluetooth connection states
enum BtConnState
{
    BT_STATE_IDLE = 0,              // BT channel is disconnected
    BT_STATE_CONN_ONGOING,          // BT channel is being connected
    BT_STATE_CONNECTED,             // BT channel is connected
    BT_STATE_DISC_ONGOING           // BT channel is being disconnected
};


// Status of Bluetooth inquiry scan
enum BtInquiryScanStatus
{
    BT_INQUIRY_SCAN_NOT_POSSIBLE = 0,
    BT_INQUIRY_SCAN_START,
    BT_INQUIRY_SCAN_RESULT,
    BT_INQUIRY_SCAN_BUSY,
    BT_INQUIRY_SCAN_TIMEOUT,
    BT_INQUIRY_SCAN_END
};


// Status codes for status field in Bluetooth callback functions
enum CB_BtStatus
{
  /*  0 */  BT_SUCCESS = 0,         // Successful end of command
  /*  1 */  BT_CON_EXIST,           // Already connected
  /*  2 */  BT_CON_SETUP,           // Establishing of connection is ongoing
  /*  3 */  BT_SWITCHED_OFF,        // Cannot connect/listen, Bluetooth is set to off
  /*  4 */  BT_ALL_CHAN_BUSY,       // Cannot connect, no more free Bluetooth channels
  /*  5 */  BT_NOT_ROBOTX,          // Cannot connect/listen, device is not a ROBO TX Controller
  /*  6 */  BT_CON_TIMEOUT,         // Cannot connect, timeout, no device with such a BT address
  /*  7 */  BT_CON_INVALID,         // Connection does not exist
  /*  8 */  BT_CON_RELEASE,         // Disconnecting is ongoing
  /*  9 */  BT_LISTEN_ACTIVE,       // Listen is already active
  /* 10 */  BT_RECEIVE_ACTIVE,      // Receive is already active
  /* 11 */  BT_CON_INDICATION,      // Passive connection establishment (incoming connection)
  /* 12 */  BT_DISCON_INDICATION,   // Passive disconnection (initiated by remote end)
  /* 13 */  BT_MSG_INDICATION,      // Received data (incoming message)
  /* 14 */  BT_CHANNEL_BUSY,        // No connect command is allowed when listen is active or
                                    // no listen command is allowed when connected
  /* 15 */  BT_BTADDR_BUSY,         // BT address is already used by another channel
  /* 16 */  BT_NO_LISTEN_ACTIVE     // Cannot connect, no active listen on remote end
};


// Identifiers of the Transfer Area
enum ta_id_e
{
    TA_LOCAL = 0,           // Transfer Area for local Controller. Corresponds to the Controller
                            // on which program is currently running in download (local) mode or
                            // to the remotely controlled Controller (seen from controlled device,
                            // not from controlling device) in online mode.
    TA_EXT_1,               // Transfer Area for Extension 1 Controller
    TA_EXT_2,               // Transfer Area for Extension 2 Controller
    TA_EXT_3,               // Transfer Area for Extension 3 Controller
    TA_EXT_4,               // Transfer Area for Extension 4 Controller
    TA_EXT_5,               // Transfer Area for Extension 5 Controller
    TA_EXT_6,               // Transfer Area for Extension 6 Controller
    TA_EXT_7,               // Transfer Area for Extension 7 Controller
    TA_EXT_8,               // Transfer Area for Extension 8 Controller
    TA_COUNT                // Number of Transfer Areas in array = 9
};

#define N_EXT               (TA_COUNT - 1)  // Number of extension Controllers = 8


// Device (Controller) functioning modes
enum dev_mode_e
{
    DEV_MODE_LOCAL = 0,
    DEV_MODE_ONLINE,
    DEV_MODE_INVALID
};


// State of connection to an extension device (Controller)
enum ext_dev_connect_state_e
{
    EXT_DEV_OFFLINE = 0,
    EXT_DEV_ONLINE,
    EXT_DEV_INVALID
};


// Modes of universal inputs
enum input_mode_e
{
    MODE_U = 0,
    MODE_R = 1,
    MODE_ULTRASONIC = 3,
    MODE_INVALID
};


// Program states
enum pgm_state_e
{
    PGM_STATE_INVALID = 0,
    PGM_STATE_RUN,
    PGM_STATE_STOP
};


// Timer units for GetSystemTime hook function
enum TimerUnit
{
    TIMER_UNIT_INVALID        = 0,
    TIMER_UNIT_SECONDS        = 2,
    TIMER_UNIT_MILLISECONDS   = 3,
    TIMER_UNIT_MICROSECONDS   = 4
};


// Bluetooth inquiry scan status
typedef struct bt_scan_status_s
{
    UINT16          status;         // Status code, see enum BtInquiryScanStatus

    // Bluetooth device info, valid only when status == BT_INQUIRY_SCAN_RESULT
    UCHAR8          bt_addr[BT_ADDR_LEN];
    char            dummy_1[2];
    char            bt_name[DEV_NAME_LEN_MAX + 1];
    char            dummy_2[3];
} BT_SCAN_STATUS;


// Structure for Bluetooth callback functions (other than receive)
typedef struct bt_cb_s
{
    UINT16          chan_idx;       // Channel index
    UINT16          status;         // Status code, see enum CB_BtStatus
} BT_CB;


// Structure for Bluetooth receive callback function
typedef struct bt_receive_cb_s
{
    UINT16          chan_idx;       // Channel index
    UINT16          status;         // Status code, see enum CB_BtStatus
    UINT16          msg_len;        // Bluetooth message length
    UCHAR8          msg[BT_MSG_LEN];// Bluetooth message
} BT_RECV_CB;


struct ta_s;

// Pointer to the Bluetooth callback function (other than receive)
typedef void (*P_CB_FUNC)(struct ta_s *, BT_CB *);

// Pointer to the Bluetooth receive callback function
typedef void (*P_RECV_CB_FUNC)(struct ta_s *, BT_RECV_CB *);



// Status codes for status field in I2C callback functions
enum CB_I2cStatus
{
  /*  0 */  I2C_SUCCESS = 0,        // Successful end of command
  /*  1 */  I2C_READ_ERROR,         // read error
  /*  2 */  I2C_WRITE_ERROR         // write error
};

// Structure for I2C callback functions
typedef struct i2c_cb_s
{
    UINT16          value;          // read/write value
    UINT16          status;         // status code, see enum CB_I2Status
} I2C_CB;

// Pointer to the I2C callback function
typedef void (*P_I2C_CB_FUNC)(struct shm_if_s *, I2C_CB *);


//=============================================================================
//  Structures for Transfer Area (TA)
//=============================================================================


// Bluetooth connection status structure, 8 bytes
typedef struct btstatus_s
{
    UINT16          conn_state;     // See enum BtConnState
    BOOL16          is_listen;      // If TRUE - BT channel is waiting for incoming connection (listening)
    BOOL16          is_receive;     // If TRUE - BT channel is ready to receive incoming messages
    UINT16          link_quality;   // 0...31, 0 - the worst, 31 - the best signal quality
} BT_STATUS;


// Program information, 8 bytes
typedef struct
{
    char          * name;   // Name of a program with a full path, for example, "/ramdisk/Program_1"
    UINT8           state;  // See enum pgm_state_e
    char            reserved[3];
} PGM_INFO;


// Display message, 128 bytes. Used to show pop-up message box on the boards display
typedef struct
{
    UINT8           id; // Should be increased by 1 each time a new pop-up message is to be shown
    char            text[DISPL_MSG_LEN_MAX + 1];
} DISPLAY_MSG;


// Display frame, 8 bytes. Used to refresh boards display with a bitmap image frame
typedef struct
{
    UCHAR8        * frame;  // Contents of a frame as a 128x64 pixels bitmap
    UINT16          id;     // Should be increased by 1 each time a new display frame is to be shown
    BOOL16          is_pgm_master_of_display;   // ++ if program wants to have control over display,
                                                // i.e. image frame is displayed over firmware menus;
                                                // -- if program wants to return control over display
                                                // to the firmware menus
} DISPLAY_FRAME;


// Version structure definition, 4 bytes
typedef union
{
    UINT32          abcd;
    struct
    {
        UCHAR8      a;
        UCHAR8      b;
        UCHAR8      c;
        UCHAR8      d;
    } part;
} FT_VER;


// Versions of hardware and firmware components, 16 bytes
typedef struct
{
    FT_VER          hardware;   // Version of hardware (hardware.part.a = 'A' or 'B' or 'C')
    FT_VER          firmware;   // Version of firmware ("V %d.%02d, DLL %d", firmware.part.c,
                                // firmware.part.d, firmware.part.b)
    FT_VER          ta;         // Version of transfer area ("V %d.%02d", ta.part.c, ta.part.d)
    char            reserved[4];
} FT_VERSION;


// Info structure, 64 bytes
typedef struct
{
    char            device_name[DEV_NAME_LEN_MAX + 1];  // Controller name
    char            bt_addr[BT_ADDR_STR_LEN + 1];       // Bluetooth address as a string
    char            reserved;
    UINT32          ta_array_start_addr;
    UINT32          pgm_area_start_addr;
    UINT32          pgm_area_size;
    FT_VERSION      version;
} TA_INFO;


// State structure, 100 bytes
typedef struct
{
    // Used by local program
    BOOL8           pgm_initialized;
    char            reserved_1[7];

    // Public state info
    BOOL8           dev_mode;   // See enum dev_mode_e
    UINT8           id;         // Should be increased by 1 each time something (except id fields and btstatus)
                                // is changed in this state structure
    UINT8           info_id;    // Should be increased by 1 each time something is changed in info structure
    UINT8           config_id;  // Should be increased by 1 each time something is changed in config structure
    BOOL8           ext_dev_connect_state[N_EXT];    // See enum ext_dev_connect_state_e
    BT_STATUS       btstatus[BT_CNT_MAX];   // Status of Bluetooth connections
    char            reserved_2[8];
    PGM_INFO        local_pgm;  // Corresponds to the program currently being in the program memory
} TA_STATE;


// Universal inputs configuration, 4 bytes
typedef struct
{
    UINT8           mode;       // See enum input_mode_e
    BOOL8           digital;    // FALSE = analog input, TRUE = digital input
    char            reserved[2];
} UNI_CONFIG;


// Counter inputs configuration, 4 bytes
typedef struct
{
    UINT8           mode;       // 0 = normal counter mode (change 0 -> 1 is counted)
                                // 1 = inverse counter mode (change 1 -> 0 is counted)
    char            reserved[3];
} CNT_CONFIG;


// Config structure, 88 bytes
typedef struct
{
    UINT8           pgm_state_req;  // See enum pgm_state_e, program state change request
    char            reserved_1[3];
    BOOL8           motor[N_MOTOR]; // TRUE = corresponding outputs are used as a pair of motor outputs M1...M4,
                                    // FALSE = corresponding outputs are used as a pair of separate digital
                                    // PWM outputs O1...O8
    UNI_CONFIG      uni[N_UNI];
    CNT_CONFIG      cnt[N_CNT];
    char            reserved_2[32];
} TA_CONFIG;


// Input structure, 68 bytes
typedef struct
{
    INT16           uni[N_UNI];             // Current values of the universal inputs
    INT16           cnt_in[N_CNT];          // Current levels (0 or 1) on the counter inputs according
                                            // to their configuration (normal or inverse)
    INT16           counter[N_CNT];         // Current values of the counter inputs
    INT16           display_button_left;    // Number of milliseconds during which the left display button
                                            // is being kept pressed
    INT16           display_button_right;   // Number of milliseconds during which the right display button
                                            // is being kept pressed
    BOOL16          cnt_resetted[N_CNT];    // Set to 1 when last requested counter reset was fulfilled
    BOOL16          motor_pos_reached[N_MOTOR]; // Set to 1 by motor control if target position
                                                // (distance from output structure) is reached
    char            reserved[16];
} TA_INPUT;


// Output structure, 44 bytes
typedef struct
{
    UINT16          cnt_reset_cmd_id[N_CNT];  // Counter reset requests (should be increased by 1 each time
                                              // counter reset is needed)
    UINT8           master[N_MOTOR];          // If not 0, synchronize this channel with the given channel
                                              // (1:channel 0, ...)
    INT16           duty[N_PWM_CHAN];         // Selected motor outputs PWM values
    UINT16          distance[N_MOTOR];        // Selected distance (counter value) at which motor shall stop
    UINT16          motor_ex_cmd_id[N_MOTOR]; // Should be increased by 1 each time settings for extended
                                              // motor control mode (duty and/or distance) are changed
} TA_OUTPUT;


// Display structure, 108 bytes
typedef struct
{
    DISPLAY_MSG     display_msg;
    DISPLAY_FRAME   display_frame;
} TA_DISPLAY;


// Status of Transfer Area (valid only for ftMscLib), 4 bytes
typedef struct
{
    UINT8           status;         // Status of transfer area
                                    //     TA_STATUS_STOP = 0 - Transfer Area is not running,
                                    //     TA_STATUS_RUN  = 1 - Transfer Area is running,
                                    //     TA_STATUS_SYNC = 2 - Transfer Area is being synchronized
    UINT8           iostatus;       // Status of I/O communication
                                    //     SE_REMIO_REQ   = 0 - Remote I/O Request was sent,
                                    //     SE_CONFIG_REQ  = 1 - Set Configuration Request was sent
    UINT16          ComErr;         // System error code by COM port connection error
} TA_STATUS;


// Change structure (valid only for ftMscLib), 8 bytes
typedef struct
{
    char            reserved_1[2];
    UINT8           ChangeStatus;   // TRUE = there was a change in any of the following fields
    UINT8           ChangeUni;      // There was a change of the input value (bit 0 = I1, bit 1 = I2, ...)
    UINT8           ChangeCntIn;    // There was a change of the counter level (bit 0 = C1, bit 1 = C2, ...)
    UINT8           ChangeCounter;  // There was a change of the counter value (bit 0 = C1, bit 1 = C2, ...)
    char            reserved_2[2];
} TA_CHANGE;


// 16-bit timers, 12 bytes
typedef struct
{
    UINT16          Timer1ms;
    UINT16          Timer10ms;
    UINT16          Timer100ms;
    UINT16          Timer1s;
    UINT16          Timer10s;
    UINT16          Timer1min;
} TA_TIMER;


// Hook table with pointers to the firmware functions,
// that can be called by local program, 132 bytes
typedef struct
{
    // Informs the calling program if it can still run (return TRUE) or should
    // immediately return to the firmware in order not to destroy the multitasking
    // mechanism of the firmware (return FALSE).
    BOOL32  (*IsRunAllowed)             (void);

    // Returns system time in seconds, milliseconds or microseconds depending on the
    // parameter unit.
    UINT32  (*GetSystemTime)            (enum TimerUnit unit);

    // Display pop-up message on the display of the ROBO TX Controller. If p_msg
    // is NULL, then all pop-up messages are removed from the display and its cache,
    // and the main frame is displayed.
    void    (*DisplayMsg)               (struct ta_s * p_ta, char * p_msg);

    // Returns TRUE if display is currently being refreshed. A program should in such a
    // case wait until the display finishes its refreshing before sending new output to it.
    BOOL32  (*IsDisplayBeingRefreshed)  (struct ta_s * p_ta);

    // Connect to the Bluetooth device with the given Bluetooth address through the given
    // channel (1...8). If p_cb_func (pointer to the callback function) is not NULL, then the
    // callback function is called to inform about the result of this command.
    void    (*BtConnect)                (UINT32 channel, UCHAR8 * btaddr, P_CB_FUNC p_cb_func);

    // Disconnect from the Bluetooth device on the given channel (1...8). If p_cb_func
    // (pointer to the callback function) is not NULL, then the callback function is called
    // to inform about the result of this command.
    void    (*BtDisconnect)             (UINT32 channel, P_CB_FUNC p_cb_func);

    // Send a message (max 255 characters) through the given Bluetooth channel (1...8).
    // If p_cb_func (pointer to the callback function) is not NULL, then the callback function is called
    // to inform about the result of this command.
    void    (*BtSend)                   (UINT32 channel, UINT32 len, UCHAR8 * p_msg, P_CB_FUNC p_cb_func);

    // Start wait for incoming messages on the given Bluetooth channel (1...8). If p_cb_func
    // (pointer to the callback function) is not NULL, then the callback function is called
    // to inform about the result of this command and about arrival of a Bluetooth message.
    void    (*BtStartReceive)           (UINT32 channel, P_RECV_CB_FUNC p_cb_func);

    // Stop wait for incoming messages on the given Bluetooth channel (1...8). If p_cb_func
    // (pointer to the callback function) is not NULL, then the callback function is called
    // to inform about the result of this command.
    void    (*BtStopReceive)            (UINT32 channel, P_RECV_CB_FUNC p_cb_func);

    // Start wait for incoming connection (i.e. listen) from the Bluetooth device with the given
    // Bluetooth address on the given channel (1...8). If p_cb_func (pointer to the callback function)
    // is not NULL, then the callback function is called to inform about the result of this command.
    void    (*BtStartListen)            (UINT32 channel, UCHAR8 * btaddr, P_CB_FUNC p_cb_func);

    // Stop wait for incoming connection (i.e. listen) on the given Bluetooth channel (1...8).
    // If p_cb_func (pointer to the callback function) is not NULL, then the callback function is called
    // to inform about the result of this command.
    void    (*BtStopListen)             (UINT32 channel, P_CB_FUNC p_cb_func);

    // Convert a Bluetooth address (6 bytes) to the string with the format "xx:xx:xx:xx:xx:xx".
    // Returns pointer to the string with converted btaddr (same pointer as str parameter).
    char   *(*BtAddrToStr)              (UCHAR8 * btaddr, char * str);

    // Interface to some runtime library functions.
    INT32   (*sprintf)                  (char * s, const char * format, ...);
    INT32   (*memcmp)                   (const void * s1, const void * s2, UINT32 n);
    void   *(*memcpy)                   (void * s1, const void * s2, UINT32 n);
    void   *(*memmove)                  (void * s1, const void * s2, UINT32 n);
    void   *(*memset)                   (void * s, INT32 c, UINT32 n);
    char   *(*strcat)                   (char * s1, const char * s2);
    char   *(*strncat)                  (char * s1, const char * s2, UINT32 n);
    char   *(*strchr)                   (const char * s, INT32 c);
    char   *(*strrchr)                  (const char * s, INT32 c);
    INT32   (*strcmp)                   (const char * s1, const char * s2);
    INT32   (*strncmp)                  (const char * s1, const char * s2, UINT32 n);
    INT32   (*stricmp)                  (const char * s1, const char * s2);
    INT32   (*strnicmp)                 (const char * s1, const char * s2, UINT32 n);
    char   *(*strcpy)                   (char * s1, const char * s2);
    char   *(*strncpy)                  (char * s1, const char * s2, UINT32 n);
    UINT32  (*strlen)                   (const char * s);
    char   *(*strstr)                   (const char * s1, const char * s2);
    char   *(*strtok)                   (char * s1, const char * s2);
    char   *(*strupr)                   (char * s);
    char   *(*strlwr)                   (char * s);
    INT32   (*atoi)                     (const char * nptr);
} TA_HOOK_TABLE;



// ============================================================================
//  Transfer Area (TA) of ROBO TX Controller (one element of TA array)
// ============================================================================
#define RESERVED_1_SIZE  28
#define RESERVED_2_SIZE \
    (1024 - ( \
    sizeof(TA_INFO)         + \
    sizeof(TA_STATE)        + \
    sizeof(TA_CONFIG)       + \
    sizeof(TA_INPUT)        + \
    sizeof(TA_OUTPUT)       + \
    sizeof(TA_DISPLAY)      + \
    sizeof(TA_STATUS)       + \
    sizeof(TA_CHANGE)       + \
    sizeof(TA_TIMER)        + \
    RESERVED_1_SIZE         + \
    sizeof(TA_HOOK_TABLE)     \
    ))


typedef struct ta_s
{
    TA_INFO             info;           // info structure
    TA_STATE            state;          // state structure
    TA_CONFIG           config;         // config structure   
    TA_INPUT            input;          // input structure
    TA_OUTPUT           output;         // output structure
    TA_DISPLAY          display;        // display structure
    TA_STATUS           status;         // status structure
    TA_CHANGE           change;         // change structure
    TA_TIMER            timer;          // 16-bit timers

    char                reserved_1[RESERVED_1_SIZE];

    TA_HOOK_TABLE       hook_table;     // hook table with functions pointers

    char                reserved_2[RESERVED_2_SIZE];
} TA;


#endif // __ROBO_TX_FW_H__
