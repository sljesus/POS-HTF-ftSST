"""
Ventana de Asignación de Turnos de Caja para HTF POS
Permite crear y asignar turnos predefinidos a empleados
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDateEdit, QLabel,
    QTimeEdit, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QDate, QTime
from PySide6.QtGui import QFont
from datetime import datetime, timedelta, time
from decimal import Decimal
import logging

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    create_page_layout,
    ContentPanel,
    StyledLabel,
    show_info_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_success_dialog,
    show_confirmation_dialog
)


class AsignacionTurnosWindow(QWidget):
    """Widget para asignar turnos de caja a empleados"""
    
    cerrar_solicitado = Signal()
    
    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.empleados = []
        self.turnos_asignados = []
        
        self.setup_ui()
        self.cargar_empleados()
        self.cargar_turnos_asignados()
    
    def setup_ui(self):
        """Configurar interfaz de asignación de turnos"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido
        content = QWidget()
        content_layout = create_page_layout("ASIGNACIÓN DE TURNOS")
        content.setLayout(content_layout)
        
        # Panel de asignación
        asignacion_panel = self.create_asignacion_panel()
        content_layout.addWidget(asignacion_panel)
        
        # Panel de turnos asignados
        tabla_panel = self.create_tabla_panel()
        content_layout.addWidget(tabla_panel)
        
        # Panel de botones
        buttons_panel = self.create_buttons_panel()
        content_layout.addWidget(buttons_panel)
        
        layout.addWidget(content)
    
    def create_asignacion_panel(self):
        """Crear panel de asignación de turnos"""
        panel = ContentPanel()
        panel_layout = QVBoxLayout(panel)
        
        # Título de sección
        title = StyledLabel("Crear Nuevo Turno", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
        panel_layout.addWidget(title)
        
        # Primera fila: Fecha y Empleado
        row1 = QHBoxLayout()
        row1.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        # Fecha
        fecha_container = QWidget()
        fecha_layout = QVBoxLayout(fecha_container)
        fecha_layout.setContentsMargins(0, 0, 0, 0)
        fecha_layout.setSpacing(5)
        
        label_fecha = StyledLabel("Fecha:", bold=True)
        fecha_layout.addWidget(label_fecha)
        
        self.fecha_turno = QDateEdit()
        self.fecha_turno.setCalendarPopup(True)
        self.fecha_turno.setDate(QDate.currentDate())
        self.fecha_turno.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.fecha_turno.setMinimumHeight(40)
        self.fecha_turno.dateChanged.connect(self.actualizar_turnos_fecha)
        fecha_layout.addWidget(self.fecha_turno)
        
        row1.addWidget(fecha_container, stretch=1)
        
        # Empleado
        empleado_container = QWidget()
        empleado_layout = QVBoxLayout(empleado_container)
        empleado_layout.setContentsMargins(0, 0, 0, 0)
        empleado_layout.setSpacing(5)
        
        label_empleado = StyledLabel("Empleado:", bold=True)
        empleado_layout.addWidget(label_empleado)
        
        self.empleado_combo = QComboBox()
        self.empleado_combo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.empleado_combo.setMinimumHeight(40)
        empleado_layout.addWidget(self.empleado_combo)
        
        row1.addWidget(empleado_container, stretch=2)
        
        panel_layout.addLayout(row1)
        
        # Segunda fila: Turno predefinido o personalizado
        row2 = QHBoxLayout()
        row2.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        # Turno predefinido
        turno_container = QWidget()
        turno_layout = QVBoxLayout(turno_container)
        turno_layout.setContentsMargins(0, 0, 0, 0)
        turno_layout.setSpacing(5)
        
        label_turno = StyledLabel("Turno:", bold=True)
        turno_layout.addWidget(label_turno)
        
        self.turno_combo = QComboBox()
        self.turno_combo.addItems([
            "Matutino (06:00 - 14:00)",
            "Vespertino (14:00 - 22:00)",
            "Personalizado"
        ])
        self.turno_combo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.turno_combo.setMinimumHeight(40)
        self.turno_combo.currentIndexChanged.connect(self.toggle_horario_personalizado)
        turno_layout.addWidget(self.turno_combo)
        
        row2.addWidget(turno_container, stretch=2)
        
        panel_layout.addLayout(row2)
        
        # Tercera fila: Horarios personalizados (ocultos por defecto)
        row3 = QHBoxLayout()
        row3.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        # Hora inicio
        inicio_container = QWidget()
        inicio_layout = QVBoxLayout(inicio_container)
        inicio_layout.setContentsMargins(0, 0, 0, 0)
        inicio_layout.setSpacing(5)
        
        self.label_inicio = StyledLabel("Hora Inicio:", bold=True)
        inicio_layout.addWidget(self.label_inicio)
        
        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setTime(QTime(6, 0))
        self.hora_inicio.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.hora_inicio.setMinimumHeight(40)
        self.hora_inicio.setDisplayFormat("HH:mm")
        inicio_layout.addWidget(self.hora_inicio)
        
        row3.addWidget(inicio_container, stretch=1)
        
        # Hora fin
        fin_container = QWidget()
        fin_layout = QVBoxLayout(fin_container)
        fin_layout.setContentsMargins(0, 0, 0, 0)
        fin_layout.setSpacing(5)
        
        self.label_fin = StyledLabel("Hora Fin:", bold=True)
        fin_layout.addWidget(self.label_fin)
        
        self.hora_fin = QTimeEdit()
        self.hora_fin.setTime(QTime(14, 0))
        self.hora_fin.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.hora_fin.setMinimumHeight(40)
        self.hora_fin.setDisplayFormat("HH:mm")
        fin_layout.addWidget(self.hora_fin)
        
        row3.addWidget(fin_container, stretch=1)
        
        # Monto inicial
        monto_container = QWidget()
        monto_layout = QVBoxLayout(monto_container)
        monto_layout.setContentsMargins(0, 0, 0, 0)
        monto_layout.setSpacing(5)
        
        label_monto = StyledLabel("Monto Inicial $:", bold=True)
        monto_layout.addWidget(label_monto)
        
        self.monto_inicial = QSpinBox()
        self.monto_inicial.setRange(0, 100000)
        self.monto_inicial.setValue(0)
        self.monto_inicial.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.monto_inicial.setMinimumHeight(40)
        monto_layout.addWidget(self.monto_inicial)
        
        row3.addWidget(monto_container, stretch=1)
        
        panel_layout.addLayout(row3)
        
        # Ocultar horarios personalizados por defecto
        self.label_inicio.hide()
        self.hora_inicio.hide()
        self.label_fin.hide()
        self.hora_fin.hide()
        
        # Botón crear turno
        btn_crear = QPushButton("Crear y Asignar Turno")
        btn_crear.setMinimumHeight(50)
        btn_crear.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        btn_crear.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #008a00;
            }}
        """)
        btn_crear.clicked.connect(self.crear_turno)
        panel_layout.addWidget(btn_crear)
        
        return panel
    
    def create_tabla_panel(self):
        """Crear panel con tabla de turnos asignados"""
        panel = ContentPanel()
        panel_layout = QVBoxLayout(panel)
        
        # Título
        title = StyledLabel("Turnos Programados", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
        panel_layout.addWidget(title)
        
        # Filtro de fecha
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        label_filtro = StyledLabel("Mostrar turnos desde:", bold=True)
        filter_layout.addWidget(label_filtro)
        
        self.fecha_filtro = QDateEdit()
        self.fecha_filtro.setCalendarPopup(True)
        self.fecha_filtro.setDate(QDate.currentDate())
        self.fecha_filtro.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.fecha_filtro.setMinimumHeight(35)
        self.fecha_filtro.dateChanged.connect(self.cargar_turnos_asignados)
        filter_layout.addWidget(self.fecha_filtro)
        
        filter_layout.addStretch()
        
        panel_layout.addLayout(filter_layout)
        
        # Tabla
        self.tabla_turnos = QTableWidget()
        self.tabla_turnos.setColumnCount(7)
        self.tabla_turnos.setHorizontalHeaderLabels([
            "Fecha", "Empleado", "Hora Inicio", "Hora Fin", 
            "Monto Inicial", "Estado", "Acciones"
        ])
        
        # Configurar tabla
        self.tabla_turnos.setAlternatingRowColors(True)
        self.tabla_turnos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_turnos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_turnos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_turnos.verticalHeader().setVisible(False)
        
        # Ajustar columnas
        header = self.tabla_turnos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Fecha
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Empleado
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Hora Inicio
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Hora Fin
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Monto
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Acciones
        
        # Estilo
        font = QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL)
        self.tabla_turnos.setFont(font)
        
        panel_layout.addWidget(self.tabla_turnos)
        
        return panel
    
    def create_buttons_panel(self):
        """Crear panel de botones"""
        panel = QWidget()
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                       WindowsPhoneTheme.MARGIN_SMALL,
                                       WindowsPhoneTheme.MARGIN_MEDIUM,
                                       WindowsPhoneTheme.MARGIN_MEDIUM)
        panel_layout.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        panel_layout.addStretch()
        
        # Botón actualizar
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setMinimumSize(150, 45)
        btn_actualizar.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        btn_actualizar.clicked.connect(self.cargar_turnos_asignados)
        panel_layout.addWidget(btn_actualizar)
        
        # Botón volver
        btn_volver = QPushButton("Volver")
        btn_volver.setMinimumSize(150, 45)
        btn_volver.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)
        panel_layout.addWidget(btn_volver)
        
        return panel
    
    def toggle_horario_personalizado(self):
        """Mostrar/ocultar campos de horario personalizado"""
        es_personalizado = self.turno_combo.currentIndex() == 2
        
        self.label_inicio.setVisible(es_personalizado)
        self.hora_inicio.setVisible(es_personalizado)
        self.label_fin.setVisible(es_personalizado)
        self.hora_fin.setVisible(es_personalizado)
        
        # Actualizar horarios según el turno seleccionado
        if not es_personalizado:
            if self.turno_combo.currentIndex() == 0:  # Matutino
                self.hora_inicio.setTime(QTime(6, 0))
                self.hora_fin.setTime(QTime(14, 0))
            elif self.turno_combo.currentIndex() == 1:  # Vespertino
                self.hora_inicio.setTime(QTime(14, 0))
                self.hora_fin.setTime(QTime(22, 0))
    
    def cargar_empleados(self):
        """Cargar lista de empleados activos"""
        try:
            with self.pg_manager.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_usuario, nombre_completo, nombre_usuario
                    FROM usuarios
                    WHERE activo = TRUE
                    ORDER BY nombre_completo
                """)
                
                self.empleados = cursor.fetchall()
                
                self.empleado_combo.clear()
                for empleado in self.empleados:
                    self.empleado_combo.addItem(
                        f"{empleado['nombre_completo']} (@{empleado['nombre_usuario']})",
                        empleado['id_usuario']
                    )
                
        except Exception as e:
            logging.error(f"Error cargando empleados: {e}")
            show_error_dialog(self, "Error", f"No se pudieron cargar los empleados: {e}")
    
    def cargar_turnos_asignados(self):
        """Cargar turnos asignados desde la fecha filtro"""
        try:
            fecha_desde = self.fecha_filtro.date().toPython()
            
            with self.pg_manager.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.id_turno,
                        t.id_usuario,
                        u.nombre_completo,
                        t.fecha_apertura,
                        t.monto_inicial,
                        t.cerrado,
                        t.fecha_cierre
                    FROM turnos_caja t
                    JOIN usuarios u ON t.id_usuario = u.id_usuario
                    WHERE DATE(t.fecha_apertura) >= %s
                    ORDER BY t.fecha_apertura DESC
                """, (fecha_desde,))
                
                self.turnos_asignados = cursor.fetchall()
                self.actualizar_tabla()
                
        except Exception as e:
            logging.error(f"Error cargando turnos asignados: {e}")
            show_error_dialog(self, "Error", f"No se pudieron cargar los turnos: {e}")
    
    def actualizar_tabla(self):
        """Actualizar contenido de la tabla de turnos"""
        self.tabla_turnos.setRowCount(len(self.turnos_asignados))
        
        for row_idx, turno in enumerate(self.turnos_asignados):
            # Fecha
            fecha = turno['fecha_apertura'].strftime("%d/%m/%Y") if turno['fecha_apertura'] else ""
            self.tabla_turnos.setItem(row_idx, 0, QTableWidgetItem(fecha))
            
            # Empleado
            self.tabla_turnos.setItem(row_idx, 1, QTableWidgetItem(turno['nombre_completo']))
            
            # Hora inicio
            hora_inicio = turno['fecha_apertura'].strftime("%H:%M") if turno['fecha_apertura'] else ""
            self.tabla_turnos.setItem(row_idx, 2, QTableWidgetItem(hora_inicio))
            
            # Hora fin (si está cerrado)
            if turno['fecha_cierre']:
                hora_fin = turno['fecha_cierre'].strftime("%H:%M")
            else:
                hora_fin = "-"
            self.tabla_turnos.setItem(row_idx, 3, QTableWidgetItem(hora_fin))
            
            # Monto inicial
            monto = f"${float(turno['monto_inicial']):.2f}"
            self.tabla_turnos.setItem(row_idx, 4, QTableWidgetItem(monto))
            
            # Estado
            estado = "CERRADO" if turno['cerrado'] else "ABIERTO"
            item_estado = QTableWidgetItem(estado)
            if not turno['cerrado']:
                item_estado.setForeground(Qt.darkGreen)
                item_estado.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
            self.tabla_turnos.setItem(row_idx, 5, item_estado)
            
            # Botón eliminar (solo si no está cerrado)
            if not turno['cerrado']:
                btn_eliminar = QPushButton("Eliminar")
                btn_eliminar.setMinimumHeight(30)
                btn_eliminar.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {WindowsPhoneTheme.TILE_RED};
                        color: white;
                        border: none;
                        border-radius: 3px;
                    }}
                    QPushButton:hover {{
                        background-color: #b30f00;
                    }}
                """)
                btn_eliminar.clicked.connect(lambda checked, id_t=turno['id_turno']: self.eliminar_turno(id_t))
                self.tabla_turnos.setCellWidget(row_idx, 6, btn_eliminar)
            else:
                self.tabla_turnos.setItem(row_idx, 6, QTableWidgetItem(""))
    
    def actualizar_turnos_fecha(self):
        """Sincronizar fecha del filtro con la fecha de creación"""
        self.fecha_filtro.setDate(self.fecha_turno.date())
    
    def crear_turno(self):
        """Crear y asignar un nuevo turno"""
        try:
            # Validar empleado seleccionado
            if self.empleado_combo.currentIndex() < 0:
                show_warning_dialog(self, "Advertencia", "Debe seleccionar un empleado")
                return
            
            id_usuario = self.empleado_combo.currentData()
            fecha_turno = self.fecha_turno.date().toPython()
            monto_inicial = self.monto_inicial.value()
            
            # Obtener horarios
            hora_inicio = self.hora_inicio.time().toPython()
            hora_fin = self.hora_fin.time().toPython()
            
            # Validar que hora fin sea después de hora inicio
            if hora_fin <= hora_inicio:
                show_warning_dialog(self, "Advertencia", "La hora de fin debe ser posterior a la hora de inicio")
                return
            
            # Crear datetime completos
            fecha_apertura = datetime.combine(fecha_turno, hora_inicio)
            
            # Verificar si ya existe un turno para ese usuario en esa fecha
            with self.pg_manager.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as cantidad
                    FROM turnos_caja
                    WHERE id_usuario = %s 
                    AND DATE(fecha_apertura) = %s
                    AND cerrado = FALSE
                """, (id_usuario, fecha_turno))
                
                resultado = cursor.fetchone()
                if resultado['cantidad'] > 0:
                    show_warning_dialog(
                        self, 
                        "Advertencia", 
                        "Ya existe un turno abierto para este empleado en esta fecha"
                    )
                    return
                
                # Confirmar creación
                turno_nombre = self.turno_combo.currentText()
                empleado_nombre = self.empleado_combo.currentText()
                
                if not show_confirmation_dialog(
                    self,
                    "Confirmar Turno",
                    f"¿Crear turno para {empleado_nombre}?",
                    detail=f"Fecha: {fecha_turno.strftime('%d/%m/%Y')}\n"
                           f"Turno: {turno_nombre}\n"
                           f"Horario: {hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}\n"
                           f"Monto inicial: ${monto_inicial:.2f}"
                ):
                    return
                
                # Insertar turno
                cursor.execute("""
                    INSERT INTO turnos_caja (
                        id_usuario,
                        fecha_apertura,
                        monto_inicial,
                        notas_apertura,
                        cerrado
                    ) VALUES (%s, %s, %s, %s, FALSE)
                """, (
                    id_usuario,
                    fecha_apertura,
                    monto_inicial,
                    f"Turno {turno_nombre}"
                ))
                
                self.pg_manager.connection.commit()
                
                show_success_dialog(self, "Éxito", "Turno creado y asignado correctamente")
                
                # Recargar turnos
                self.cargar_turnos_asignados()
                
        except Exception as e:
            self.pg_manager.connection.rollback()
            logging.error(f"Error creando turno: {e}")
            show_error_dialog(self, "Error", f"No se pudo crear el turno: {e}")
    
    def eliminar_turno(self, id_turno):
        """Eliminar un turno programado que no ha iniciado"""
        try:
            if not show_confirmation_dialog(
                self,
                "Confirmar Eliminación",
                "¿Está seguro de eliminar este turno programado?"
            ):
                return
            
            with self.pg_manager.connection.cursor() as cursor:
                # Verificar que el turno no esté cerrado
                cursor.execute("""
                    SELECT cerrado FROM turnos_caja WHERE id_turno = %s
                """, (id_turno,))
                
                turno = cursor.fetchone()
                if turno and turno['cerrado']:
                    show_warning_dialog(self, "Advertencia", "No se puede eliminar un turno cerrado")
                    return
                
                # Eliminar turno
                cursor.execute("""
                    DELETE FROM turnos_caja WHERE id_turno = %s
                """, (id_turno,))
                
                self.pg_manager.connection.commit()
                
                show_success_dialog(self, "Éxito", "Turno eliminado correctamente")
                
                # Recargar tabla
                self.cargar_turnos_asignados()
                
        except Exception as e:
            self.pg_manager.connection.rollback()
            logging.error(f"Error eliminando turno: {e}")
            show_error_dialog(self, "Error", f"No se pudo eliminar el turno: {e}")
